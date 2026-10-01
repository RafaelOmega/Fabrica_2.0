# -*- coding: utf-8 -*-
"""Repositório de saídas: acesso a dados (PostgreSQL).

Schema:
  saidas       (id, sequencia, data_saida)
  itens_saida  (id, saida_id, produto_id, quantidade, custo)
  itens_saida_mao_obra (id, saida_id, produto_id, quantidade, custo)
  movimentos_kardex  (espelho: tipo 'S' com saida_id preenchido)

A mão de obra da saída é persistida em itens_saida_mao_obra e NÃO
gera movimento no kardex (não controla estoque).
"""
from datetime import date

from app.database import get_connection
from app.models.saida import ItemSaida, ItemSaidaMaoObra, Saida
from app.utils.logger import get_logger

logger = get_logger("saida_repository")

_COLUNAS = "sequencia, data_saida"
_COLUNAS_ITEM = "saida_id, produto_id, quantidade, custo"
_COLUNAS_MAO_OBRA = "saida_id, produto_id, quantidade, custo"


class SaidaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, saida: Saida) -> Saida:
        """Grava cabeçalho + itens + mão de obra + kardex em transação única."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO saidas ({_COLUNAS}) "
                    "VALUES ((SELECT COALESCE(MAX(sequencia), 0) + 1 "
                    "FROM saidas), %s) "
                    "RETURNING id, sequencia",
                    (date.fromisoformat(saida.data_saida),),
                )
                linha = cur.fetchone()
                saida.id, saida.sequencia = linha[0], linha[1]
                self._inserir_itens(cur, saida)
                self._inserir_kardex(cur, saida)
                self._inserir_mao_obra(cur, saida)
        logger.info("Saída inserida: id=%s sequencia=%s (%s itens, %s mão de obra)",
                    saida.id, saida.sequencia,
                    len(saida.itens), len(saida.mao_obra))
        return saida

    def atualizar(self, saida: Saida) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "UPDATE saidas SET data_saida = %s WHERE id = %s",
                    (date.fromisoformat(saida.data_saida), saida.id),
                )
                cur.execute(
                    "DELETE FROM itens_saida WHERE saida_id = %s",
                    (saida.id,),
                )
                self._inserir_itens(cur, saida)
                # kardex: regrava o espelho das baixas
                cur.execute(
                    "DELETE FROM movimentos_kardex WHERE saida_id = %s",
                    (saida.id,),
                )
                self._inserir_kardex(cur, saida)
                # mão de obra: regrava a lista completa
                cur.execute(
                    "DELETE FROM itens_saida_mao_obra WHERE saida_id = %s",
                    (saida.id,),
                )
                self._inserir_mao_obra(cur, saida)
        logger.info("Saída atualizada: id=%s", saida.id)
        return True

    def excluir(self, saida_id: int) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                # remove o espelho no kardex
                cur.execute(
                    "DELETE FROM movimentos_kardex WHERE saida_id = %s",
                    (saida_id,),
                )
                # remove a mão de obra
                cur.execute(
                    "DELETE FROM itens_saida_mao_obra WHERE saida_id = %s",
                    (saida_id,),
                )
                # remove os itens (FK sem CASCADE em bancos antigos)
                cur.execute(
                    "DELETE FROM itens_saida WHERE saida_id = %s",
                    (saida_id,),
                )
                cur.execute(
                    "DELETE FROM saidas WHERE id = %s",
                    (saida_id,),
                )
        logger.info("Saída excluída: id=%s", saida_id)
        return True

    # ---------------- auxiliares de escrita ----------------

    def _inserir_itens(self, cur, saida: Saida):
        for item in saida.itens:
            if item.produto_id is None:
                continue
            cur.execute(
                f"INSERT INTO itens_saida ({_COLUNAS_ITEM}) "
                "VALUES (%s, %s, %s, %s)",
                (saida.id, item.produto_id, item.quantidade, item.custo),
            )

    def _inserir_mao_obra(self, cur, saida: Saida):
        """Grava a mão de obra da saída (não vai ao kardex)."""
        for mo in saida.mao_obra:
            if mo.produto_id is None:
                continue
            cur.execute(
                f"INSERT INTO itens_saida_mao_obra ({_COLUNAS_MAO_OBRA}) "
                "VALUES (%s, %s, %s, %s)",
                (saida.id, mo.produto_id, mo.quantidade, mo.custo),
            )

    def _inserir_kardex(self, cur, saida: Saida):
        """Espelha os itens na tabela movimentos_kardex (tipo 'S')."""
        for item in saida.itens:
            if item.produto_id is None:
                continue
            cur.execute(
                "INSERT INTO movimentos_kardex "
                "(produto_id, data_movimento, tipo, documento, historico, "
                "quantidade, custo_unitario, saida_id) "
                "VALUES (%s, %s, 'S', %s, %s, %s, %s, %s)",
                (item.produto_id,
                 date.fromisoformat(saida.data_saida),
                 str(saida.sequencia), "Saída",
                 item.quantidade, item.custo, saida.id),
            )

    # ---------------- leitura ----------------

    def buscar_por_id(self, saida_id: int) -> Saida | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT id, sequencia, data_saida "
                    "FROM saidas WHERE id = %s",
                    (saida_id,),
                )
                linha = cur.fetchone()
                if not linha:
                    return None
                saida = self._linha_para_saida(linha)
                saida.itens = self._buscar_itens(cur, saida.id)
                saida.mao_obra = self._buscar_mao_obra(cur, saida.id)
        return saida

    def buscar_por_sequencia(self, sequencia: int) -> Saida | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT id, sequencia, data_saida "
                    "FROM saidas WHERE sequencia = %s",
                    (sequencia,),
                )
                linha = cur.fetchone()
                if not linha:
                    return None
                saida = self._linha_para_saida(linha)
                saida.itens = self._buscar_itens(cur, saida.id)
                saida.mao_obra = self._buscar_mao_obra(cur, saida.id)
        return saida

    def pesquisar(self, filtro: str = "") -> list[Saida]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.id, s.sequencia, s.data_saida,
                           (SELECT COALESCE(SUM(quantidade * custo), 0)
                              FROM itens_saida
                             WHERE saida_id = s.id) AS total
                      FROM saidas s
                     WHERE CAST(s.sequencia AS TEXT) ILIKE %s
                        OR to_char(s.data_saida, 'DD/MM/YYYY') ILIKE %s
                     ORDER BY s.sequencia DESC
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [s for s in (self._linha_para_saida(l) for l in linhas) if s]

    def saldo_atual(self, produto_id: int) -> float:
        """Posição do produto no kardex: entradas - saídas."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(SUM(
                               CASE WHEN tipo = 'E' THEN quantidade
                                    ELSE -quantidade END), 0)
                      FROM movimentos_kardex
                     WHERE produto_id = %s
                    """,
                    (produto_id,),
                )
                linha = cur.fetchone()
        return float(linha[0]) if linha and linha[0] is not None else 0.0

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_saida(linha) -> Saida | None:
        if not linha:
            return None
        saida = Saida(
            id=linha[0],
            sequencia=linha[1],
            data_saida=(linha[2].isoformat()
                        if hasattr(linha[2], "isoformat")
                        else str(linha[2] or "")),
        )
        if len(linha) > 3 and linha[3] is not None:
            saida.total_sql = float(linha[3])
        return saida

    @staticmethod
    def _buscar_itens(cur, saida_id: int) -> list[ItemSaida]:
        cur.execute(
            "SELECT is_.id, is_.saida_id, is_.produto_id, p.codigo, "
            "p.descricao, is_.quantidade, is_.custo "
            "FROM itens_saida is_ "
            "LEFT JOIN produtos p ON p.id = is_.produto_id "
            "WHERE is_.saida_id = %s ORDER BY is_.id",
            (saida_id,),
        )
        return [
            ItemSaida(
                id=l[0], saida_id=l[1], produto_id=l[2],
                codigo_produto=l[3] or "",
                descricao_produto=l[4] or "",
                quantidade=float(l[5]), custo=float(l[6]),
            )
            for l in cur.fetchall()
        ]

    @staticmethod
    def _buscar_mao_obra(cur, saida_id: int) -> list[ItemSaidaMaoObra]:
        cur.execute(
            "SELECT m.id, m.saida_id, m.produto_id, p.codigo, "
            "p.descricao, m.quantidade, m.custo "
            "FROM itens_saida_mao_obra m "
            "LEFT JOIN produtos p ON p.id = m.produto_id "
            "WHERE m.saida_id = %s ORDER BY m.id",
            (saida_id,),
        )
        return [
            ItemSaidaMaoObra(
                id=l[0], saida_id=l[1], produto_id=l[2],
                codigo_produto=l[3] or "",
                descricao_produto=l[4] or "",
                quantidade=float(l[5]), custo=float(l[6]),
            )
            for l in cur.fetchall()
        ]
