# -*- coding: utf-8 -*-
"""Repositório de entradas: acesso a dados (PostgreSQL).

Schema:
  entradas           (id, sequencia, data_entrada, motivo_entrada_id)
  itens_entrada      (id, entrada_id, produto_id, quantidade, custo)
  movimentos_kardex  (espelho dos movimentos: entradas 'E' e baixas 'S')
"""
from datetime import date

from app.database import get_connection
from app.models.entrada import Entrada, ItemEntrada
from app.utils.logger import get_logger

from app.services.regras_entrada import custo_diverge

logger = get_logger("entrada_repository")

_COLUNAS = "sequencia, data_entrada, motivo_entrada_id"
_COLUNAS_ITEM = "entrada_id, produto_id, quantidade, custo"


class EntradaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, entrada: Entrada) -> Entrada:
        """Grava cabeçalho + itens + kardex em transação única."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO entradas ({_COLUNAS}) "
                    "VALUES ((SELECT COALESCE(MAX(sequencia), 0) + 1 "
                    "FROM entradas), %s, %s) "
                    "RETURNING id, sequencia",
                    (date.fromisoformat(entrada.data_entrada),
                     entrada.motivo_id),
                )
                linha = cur.fetchone()
                entrada.id, entrada.sequencia = linha[0], linha[1]
                self._inserir_itens(cur, entrada)
                self._inserir_kardex(cur, entrada)
        logger.info("Entrada inserida: id=%s sequencia=%s (%s itens)",
                    entrada.id, entrada.sequencia, len(entrada.itens))
        return entrada

    def atualizar(self, entrada: Entrada) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "UPDATE entradas SET data_entrada = %s, "
                    "motivo_entrada_id = %s WHERE id = %s",
                    (date.fromisoformat(entrada.data_entrada),
                     entrada.motivo_id, entrada.id),
                )
                cur.execute(
                    "DELETE FROM itens_entrada WHERE entrada_id = %s",
                    (entrada.id,),
                )
                self._inserir_itens(cur, entrada)
                # kardex: regrava o espelho (entradas 'E' e baixas 'S')
                cur.execute(
                    "DELETE FROM movimentos_kardex WHERE entrada_id = %s",
                    (entrada.id,),
                )
                self._inserir_kardex(cur, entrada)
        logger.info("Entrada atualizada: id=%s", entrada.id)
        return True

    def excluir(self, entrada_id: int) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                # desfaz alterações de custo geradas por esta entrada
                cur.execute(
                    "SELECT produto_id, custo_anterior, custo_novo "
                    "FROM alteracoes_custo WHERE entrada_id = %s",
                    (entrada_id,),
                )
                for produto_id, custo_anterior, custo_novo in cur.fetchall():
                    cur.execute(
                        "SELECT custo FROM produtos WHERE id = %s",
                        (produto_id,),
                    )
                    linha = cur.fetchone()
                    if linha is None:
                        continue
                    custo_atual = float(linha[0])
                    # só reverte se nenhuma alteração posterior sobrescreveu
                    if not custo_diverge(custo_atual, float(custo_novo)):
                        cur.execute(
                            "UPDATE produtos SET custo = %s WHERE id = %s",
                            (custo_anterior, produto_id),
                        )
                # remove o espelho no kardex (entradas e baixas de produção)
                cur.execute(
                    "DELETE FROM movimentos_kardex WHERE entrada_id = %s",
                    (entrada_id,),
                )
                # remove os registros de auditoria da entrada excluída
                cur.execute(
                    "DELETE FROM alteracoes_custo WHERE entrada_id = %s",
                    (entrada_id,),
                )
                # remove os itens da entrada (FK sem CASCADE no banco real)
                cur.execute(
                    "DELETE FROM itens_entrada WHERE entrada_id = %s",
                    (entrada_id,),
                )
                cur.execute(
                    "DELETE FROM entradas WHERE id = %s",
                    (entrada_id,),
                )
        logger.info("Entrada excluída: id=%s", entrada_id)
        return True

    # ---------------- correção de lançamentos (ficha técnica) ----------------

    def entradas_de_producao(self, produto_id: int | None) -> list[int]:
        """Entradas de produção (motivo baixa_producao) com o produto acabado.

        Usado ao alterar uma ficha técnica: são as entradas cujas baixas
        foram calculadas com a ficha.
        """
        if produto_id is None:
            return []
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT e.id, e.sequencia
                      FROM entradas e
                      JOIN motivos_entrada m ON m.id = e.motivo_entrada_id
                      JOIN itens_entrada ie ON ie.entrada_id = e.id
                     WHERE m.baixa_producao = TRUE
                       AND ie.produto_id = %s
                     ORDER BY e.sequencia
                    """,
                    (produto_id,),
                )
                return [l[0] for l in cur.fetchall()]

    def recalcular_baixas(self, entrada_id: int) -> bool:
        """Regrava as baixas de produção da entrada com as fichas atuais.

        Para cada acabado da entrada com ficha técnica válida:
          - recalcula as baixas (proporção sacos_batida) com a ficha vigente
          - atualiza o custo do acabado nos lançamentos
            (itens_entrada + kardex 'E')
          - regrava os movimentos 'S' (baixas) da entrada no kardex
        Entradas sem motivo de produção ou sem acabado com ficha ficam
        intactas (devolve False).
        """
        from app.repositories.ficha_tecnica_repository import (
            FichaTecnicaRepository,
        )
        from app.services import regras_producao

        # ---- 1) leitura: entrada é de produção? quais os itens? ----
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT e.data_entrada, e.sequencia, "
                    "COALESCE(m.baixa_producao, FALSE), "
                    "COALESCE(m.descricao, '') "
                    "FROM entradas e "
                    "LEFT JOIN motivos_entrada m "
                    "  ON m.id = e.motivo_entrada_id "
                    "WHERE e.id = %s",
                    (entrada_id,),
                )
                linha = cur.fetchone()
                if not linha:
                    return False
                data_entrada, sequencia, baixa_producao, historico = linha
                if not baixa_producao:
                    return False
                cur.execute(
                    "SELECT ie.id, ie.produto_id, ie.quantidade "
                    "FROM itens_entrada ie "
                    "WHERE ie.entrada_id = %s ORDER BY ie.id",
                    (entrada_id,),
                )
                itens = cur.fetchall()

        # ---- 2) fichas atuais de cada acabado (fora da transação) ----
        ficha_repo = FichaTecnicaRepository(conn=self._conn)
        acabados = []  # (item_id, produto_id, baixas)
        for item_id, produto_id, quantidade in itens:
            if produto_id is None:
                continue
            ficha = ficha_repo.buscar_por_produto(produto_id)
            if not regras_producao.ficha_valida(ficha):
                continue
            acabados.append((item_id, produto_id,
                             regras_producao.calcular_baixa(
                                 ficha, float(quantidade))))
        if not acabados:
            return False

        # ---- 3) escrita: custos + regravação das baixas ----
        with self._conn:
            with self._conn.cursor() as cur:
                for item_id, produto_id, baixas in acabados:
                    custo_novo = regras_producao.custo_producao(
                        baixas, self._custos_insumos(cur, baixas))
                    cur.execute(
                        "UPDATE itens_entrada SET custo = %s WHERE id = %s",
                        (custo_novo, item_id),
                    )
                    cur.execute(
                        "UPDATE movimentos_kardex SET custo_unitario = %s "
                        "WHERE entrada_id = %s AND tipo = 'E' "
                        "AND produto_id = %s",
                        (custo_novo, entrada_id, produto_id),
                    )
                cur.execute(
                    "DELETE FROM movimentos_kardex "
                    "WHERE entrada_id = %s AND tipo = 'S'",
                    (entrada_id,),
                )
                for _, _, baixas in acabados:
                    for baixa in baixas:
                        cur.execute(
                            "SELECT custo FROM produtos WHERE id = %s",
                            (baixa.produto_id,),
                        )
                        linha_custo = cur.fetchone()
                        custo_insumo = (
                            float(linha_custo[0])
                            if linha_custo and linha_custo[0] is not None
                            else 0.0)
                        cur.execute(
                            "INSERT INTO movimentos_kardex "
                            "(produto_id, data_movimento, tipo, documento, "
                            "historico, quantidade, custo_unitario, "
                            "entrada_id) VALUES (%s, %s, 'S', %s, %s, "
                            "%s, %s, %s)",
                            (baixa.produto_id, data_entrada, str(sequencia),
                             f"Baixa produção - {historico}",
                             # quantidade convertida para sacos
                             baixa.quantidade_sacos
                             if baixa.quantidade_sacos
                             else baixa.quantidade_kg,
                             custo_insumo, entrada_id),
                        )
        logger.info("Baixas recalculadas na entrada id=%s (%s acabados)",
                    entrada_id, len(acabados))
        return True

    @staticmethod
    def _custos_insumos(cur, baixas) -> dict[str, float]:
        """Custo cadastrado atual de cada insumo (por código)."""
        custos: dict[str, float] = {}
        for baixa in baixas:
            if baixa.produto_id is None or baixa.codigo_produto in custos:
                continue
            cur.execute(
                "SELECT custo FROM produtos WHERE id = %s",
                (baixa.produto_id,),
            )
            linha = cur.fetchone()
            custos[baixa.codigo_produto] = (
                float(linha[0])
                if linha and linha[0] is not None else 0.0)
        return custos

    # ---------------- auxiliares de escrita ----------------

    def _inserir_itens(self, cur, entrada: Entrada):
        for item in entrada.itens:
            if item.produto_id is None:
                continue
            cur.execute(
                f"INSERT INTO itens_entrada ({_COLUNAS_ITEM}) "
                "VALUES (%s, %s, %s, %s)",
                (entrada.id, item.produto_id, item.quantidade, item.custo),
            )
            # regra: custo divergente -> atualiza cadastro e registra
            cur.execute(
                "SELECT custo FROM produtos WHERE id = %s",
                (item.produto_id,),
            )
            linha = cur.fetchone()
            if linha is None:
                continue
            custo_cadastrado = float(linha[0])
            if custo_diverge(custo_cadastrado, item.custo):
                cur.execute(
                    "UPDATE produtos SET custo = %s WHERE id = %s",
                    (item.custo, item.produto_id),
                )
                cur.execute(
                    "INSERT INTO alteracoes_custo "
                    "(produto_id, custo_anterior, custo_novo, origem, "
                    "entrada_id) VALUES (%s, %s, %s, 'entrada', %s)",
                    (item.produto_id, custo_cadastrado, item.custo,
                     entrada.id),
                )

    def _inserir_kardex(self, cur, entrada: Entrada):
        """Espelha os movimentos na tabela movimentos_kardex.

        Entradas dos itens viram tipo 'E'; as baixas de produção
        (insumos consumidos pela ficha técnica) viram tipo 'S'
        vinculadas ao entrada_id, com a quantidade já convertida
        para sacos.
        """
        cur.execute(
            "SELECT descricao FROM motivos_entrada WHERE id = %s",
            (entrada.motivo_id,),
        )
        linha = cur.fetchone()
        historico = (linha[0] if linha else "") or entrada.motivo_descricao

        # entradas dos itens (tipo 'E')
        for item in entrada.itens:
            if item.produto_id is None:
                continue
            cur.execute(
                "INSERT INTO movimentos_kardex "
                "(produto_id, data_movimento, tipo, documento, historico, "
                "quantidade, custo_unitario, entrada_id) "
                "VALUES (%s, %s, 'E', %s, %s, %s, %s, %s)",
                (item.produto_id,
                 date.fromisoformat(entrada.data_entrada),
                 str(entrada.sequencia), historico,
                 item.quantidade, item.custo, entrada.id),
            )

        # baixa de produção: consome os insumos da ficha técnica (tipo 'S')
        for baixa in getattr(entrada, "baixas", []):
            if baixa.produto_id is None:
                continue
            cur.execute(
                "SELECT custo FROM produtos WHERE id = %s",
                (baixa.produto_id,),
            )
            linha_custo = cur.fetchone()
            custo_insumo = (float(linha_custo[0])
                            if linha_custo and linha_custo[0] is not None
                            else 0.0)
            cur.execute(
                "INSERT INTO movimentos_kardex "
                "(produto_id, data_movimento, tipo, documento, historico, "
                "quantidade, custo_unitario, entrada_id) "
                "VALUES (%s, %s, 'S', %s, %s, %s, %s, %s)",
                (baixa.produto_id,
                 date.fromisoformat(entrada.data_entrada),
                 str(entrada.sequencia),
                 f"Baixa produção - {historico}",
                 # quantidade convertida para sacos
                 baixa.quantidade_sacos if baixa.quantidade_sacos else
                 baixa.quantidade_kg,
                 custo_insumo, entrada.id),
            )

    # ---------------- leitura ----------------

    def buscar_por_id(self, entrada_id: int) -> Entrada | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT e.id, e.sequencia, e.data_entrada, "
                    "e.motivo_entrada_id, m.codigo, m.descricao "
                    "FROM entradas e "
                    "LEFT JOIN motivos_entrada m "
                    "  ON m.id = e.motivo_entrada_id "
                    "WHERE e.id = %s",
                    (entrada_id,),
                )
                linha = cur.fetchone()
                if not linha:
                    return None
                entrada = self._linha_para_entrada(linha)
                entrada.itens = self._buscar_itens(cur, entrada.id)
        return entrada

    def buscar_por_sequencia(self, sequencia: int) -> Entrada | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT e.id, e.sequencia, e.data_entrada, "
                    "e.motivo_entrada_id, m.codigo, m.descricao "
                    "FROM entradas e "
                    "LEFT JOIN motivos_entrada m "
                    "  ON m.id = e.motivo_entrada_id "
                    "WHERE e.sequencia = %s",
                    (sequencia,),
                )
                linha = cur.fetchone()
                if not linha:
                    return None
                entrada = self._linha_para_entrada(linha)
                entrada.itens = self._buscar_itens(cur, entrada.id)
        return entrada

    def pesquisar(self, filtro: str = "") -> list[Entrada]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.id, e.sequencia, e.data_entrada,
                           e.motivo_entrada_id, m.codigo, m.descricao,
                           (SELECT COALESCE(SUM(quantidade * custo), 0)
                              FROM itens_entrada
                             WHERE entrada_id = e.id) AS total
                      FROM entradas e
                      LEFT JOIN motivos_entrada m
                        ON m.id = e.motivo_entrada_id
                     WHERE CAST(e.sequencia AS TEXT) ILIKE %s
                        OR m.codigo ILIKE %s
                        OR m.descricao ILIKE %s
                     ORDER BY e.sequencia DESC
                    """,
                    (termo, termo, termo),
                )
                linhas = cur.fetchall()
        return [e for e in (self._linha_para_entrada(l) for l in linhas) if e]

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_entrada(linha) -> Entrada | None:
        if not linha:
            return None
        entrada = Entrada(
            id=linha[0],
            sequencia=linha[1],
            data_entrada=(linha[2].isoformat()
                          if hasattr(linha[2], "isoformat")
                          else str(linha[2] or "")),
            motivo_id=linha[3],
            motivo_codigo=linha[4] or "",
            motivo_descricao=linha[5] or "",
        )
        if len(linha) > 6 and linha[6] is not None:
            entrada.total_sql = float(linha[6])
        return entrada

    @staticmethod
    def _buscar_itens(cur, entrada_id: int) -> list[ItemEntrada]:
        cur.execute(
            "SELECT ie.id, ie.entrada_id, ie.produto_id, p.codigo, "
            "p.descricao, ie.quantidade, ie.custo "
            "FROM itens_entrada ie "
            "LEFT JOIN produtos p ON p.id = ie.produto_id "
            "WHERE ie.entrada_id = %s ORDER BY ie.id",
            (entrada_id,),
        )
        return [
            ItemEntrada(
                id=l[0], entrada_id=l[1], produto_id=l[2],
                codigo_produto=l[3] or "",
                descricao_produto=l[4] or "",
                quantidade=float(l[5]), custo=float(l[6]),
            )
            for l in cur.fetchall()
        ]
