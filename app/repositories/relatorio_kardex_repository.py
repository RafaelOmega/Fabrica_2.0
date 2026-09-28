# -*- coding: utf-8 -*-
"""Repositório do relatório de kardex (PostgreSQL).

Fonte atual: entradas (itens_entrada + entradas + motivos_entrada).
Preparado para saídas: quando a tabela de saídas existir, basta
acrescentar o UNION ALL indicado em _movimentos — model, service,
PDF, preview e exportação não mudam (o tipo "S" já é tratado).
"""
from datetime import date

from app.database import get_connection
from app.models.relatorio_kardex import (
    KardexProduto, MovimentoKardex, TIPO_ENTRADA,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_kardex_repository")


class RelatorioKardexRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def kardex(self, filtro: str, data_inicial: date,
               data_final: date) -> list[KardexProduto]:
        """Kardex por produto no período.

        Filtro vazio: todos os produtos com movimentação no período.
        Filtro preenchido: o produto pelo código ou descrição (mesmo
        sem movimentos no período).
        """
        produtos = self._produtos_do_relatorio(
            filtro, data_inicial, data_final)
        with self._conn:
            with self._conn.cursor() as cur:
                for produto in produtos:
                    produto.saldo_inicial = self._saldo_inicial(
                        cur, produto.produto_id, data_inicial)
                    produto.movimentos = self._movimentos(
                        cur, produto.produto_id, data_inicial, data_final)
        logger.info("Kardex: %s produto(s) no período", len(produtos))
        return produtos

    # ---------------- auxiliares ----------------

    @staticmethod
    def _produtos_do_relatorio(filtro: str, data_inicial: date,
                               data_final: date) -> list[KardexProduto]:
        termo = f"%{filtro}%"
        with get_connection() as conn:
            with conn.cursor() as cur:
                if filtro:
                    cur.execute(
                        """
                        SELECT id, codigo, descricao
                          FROM produtos
                         WHERE codigo ILIKE %s OR descricao ILIKE %s
                         ORDER BY descricao
                        """,
                        (termo, termo),
                    )
                else:
                    cur.execute(
                        """
                        SELECT DISTINCT p.id, p.codigo, p.descricao
                          FROM produtos p
                          JOIN itens_entrada ie ON ie.produto_id = p.id
                          JOIN entradas e ON e.id = ie.entrada_id
                         WHERE e.data_entrada BETWEEN %s AND %s
                         ORDER BY p.descricao
                        """,
                        (data_inicial, data_final),
                    )
                return [
                    KardexProduto(
                        produto_id=l[0], codigo=l[1],
                        descricao=l[2] or "",
                    )
                    for l in cur.fetchall()
                ]

    @staticmethod
    def _saldo_inicial(cur, produto_id: int, data_inicial: date) -> float:
        """Entradas anteriores à data inicial.

        TODO (Saída): subtrair também as saídas anteriores à data inicial.
        """
        cur.execute(
            """
            SELECT COALESCE(SUM(ie.quantidade), 0)
              FROM itens_entrada ie
              JOIN entradas e ON e.id = ie.entrada_id
             WHERE ie.produto_id = %s
               AND e.data_entrada < %s
            """,
            (produto_id, data_inicial),
        )
        return float(cur.fetchone()[0])

    @staticmethod
    def _movimentos(cur, produto_id: int, data_inicial: date,
                    data_final: date) -> list[MovimentoKardex]:
        cur.execute(
            """
            SELECT e.data_entrada, e.sequencia,
                   COALESCE(m.descricao, ''), ie.quantidade, ie.custo
              FROM itens_entrada ie
              JOIN entradas e ON e.id = ie.entrada_id
              LEFT JOIN motivos_entrada m ON m.id = e.motivo_entrada_id
             WHERE ie.produto_id = %s
               AND e.data_entrada BETWEEN %s AND %s
             ORDER BY e.data_entrada, e.sequencia, ie.id
            """,
            (produto_id, data_inicial, data_final),
        )
        # TODO (Saída): UNION ALL com o mesmo SELECT sobre a tabela de
        # saídas (tipo "S"), mantendo a ordenação por data/documento.
        return [
            MovimentoKardex(
                data=l[0].isoformat() if hasattr(l[0], "isoformat")
                else str(l[0]),
                documento=str(l[1]),
                historico=l[2] or "",
                tipo=TIPO_ENTRADA,
                quantidade=float(l[3]),
                custo_unitario=float(l[4]) if l[4] is not None else None,
            )
            for l in cur.fetchall()
        ]
