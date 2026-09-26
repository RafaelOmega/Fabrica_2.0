# -*- coding: utf-8 -*-
"""Repositório de entradas: acesso a dados (PostgreSQL).

Schema:
  entradas       (id, sequencia, data_entrada, motivo_entrada_id)
  itens_entrada  (id, entrada_id, produto_id, quantidade, custo)
"""
from datetime import date

from app.database import get_connection
from app.models.entrada import Entrada, ItemEntrada
from app.utils.logger import get_logger

logger = get_logger("entrada_repository")

_COLUNAS = "sequencia, data_entrada, motivo_entrada_id"
_COLUNAS_ITEM = "entrada_id, produto_id, quantidade, custo"


class EntradaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, entrada: Entrada) -> Entrada:
        """Grava cabeçalho + itens em transação única. Retorna com id."""
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
        logger.info("Entrada atualizada: id=%s", entrada.id)
        return True

    def excluir(self, entrada_id: int) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM itens_entrada WHERE entrada_id = %s",
                    (entrada_id,),
                )
                cur.execute(
                    "DELETE FROM entradas WHERE id = %s", (entrada_id,))
        logger.info("Entrada excluída: id=%s", entrada_id)
        return True

    @staticmethod
    def _inserir_itens(cur, entrada: Entrada):
        for item in entrada.itens:
            cur.execute(
                f"INSERT INTO itens_entrada ({_COLUNAS_ITEM}) "
                "VALUES (%s, %s, %s, %s)",
                (entrada.id, item.produto_id, item.quantidade, item.custo),
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

    @staticmethod
    def _buscar_itens(cur, entrada_id: int) -> list[ItemEntrada]:
        cur.execute(
            "SELECT ie.id, ie.entrada_id, ie.produto_id, p.codigo, "
            "ie.quantidade, ie.custo "
            "FROM itens_entrada ie "
            "LEFT JOIN produtos p ON p.id = ie.produto_id "
            "WHERE ie.entrada_id = %s ORDER BY ie.id",
            (entrada_id,),
        )
        return [
            ItemEntrada(
                id=l[0], entrada_id=l[1], produto_id=l[2],
                codigo_produto=l[3] or "", quantidade=float(l[4]),
                custo=float(l[5]),
            )
            for l in cur.fetchall()
        ]

    @staticmethod
    def _linha_para_entrada(linha) -> Entrada | None:
        if not linha:
            return None
        data = linha[2]
        return Entrada(
            id=linha[0],
            sequencia=linha[1],
            data_entrada=data.isoformat() if isinstance(data, date) else str(data),
            motivo_id=linha[3],
            motivo_codigo=linha[4] or "",
            motivo_descricao=linha[5] or "",
        )
