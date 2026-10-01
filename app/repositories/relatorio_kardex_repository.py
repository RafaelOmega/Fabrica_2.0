# -*- coding: utf-8 -*-
"""Repositório do relatório de kardex (PostgreSQL).

Fonte: tabela movimentos_kardex (espelho dos movimentos).
As quantidades já são gravadas na unidade correta no kardex:
  - Entrada (tipo 'E'): kg de compra / como lançada
  - Baixa de produção (tipo 'S'): sacos (convertido pela ficha técnica)
Este repositório apenas lê os valores como foram gravados, sem
conversão. A unidade do produto (ex.: saco) é exibida para referência.
"""
from datetime import date

from app.database import get_connection
from app.models.relatorio_kardex import (
    KardexProduto, MovimentoKardex, TIPO_ENTRADA, TIPO_SAIDA,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_kardex_repository")


class RelatorioKardexRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def kardex(self, filtro: str, data_inicial: date,
               data_final: date) -> list[KardexProduto]:
        """Kardex por produto no período (valores como gravados).

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
                        SELECT p.id, p.codigo, p.descricao,
                               COALESCE(um.descricao, 'kg')
                          FROM produtos p
                          LEFT JOIN unidades_medida um
                            ON um.codigo = p.unidade
                         WHERE p.codigo ILIKE %s OR p.descricao ILIKE %s
                         ORDER BY p.descricao
                        """,
                        (termo, termo),
                    )
                else:
                    cur.execute(
                        """
                        SELECT DISTINCT p.id, p.codigo, p.descricao,
                               COALESCE(um.descricao, 'kg')
                          FROM produtos p
                          JOIN movimentos_kardex mk
                            ON mk.produto_id = p.id
                          LEFT JOIN unidades_medida um
                            ON um.codigo = p.unidade
                         WHERE mk.data_movimento BETWEEN %s AND %s
                         ORDER BY p.descricao
                        """,
                        (data_inicial, data_final),
                    )
                return [
                    KardexProduto(
                        produto_id=l[0], codigo=l[1],
                        descricao=l[2] or "",
                        unidade=l[3] or "kg",
                    )
                    for l in cur.fetchall()
                ]

    @staticmethod
    def _saldo_inicial(cur, produto_id: int, data_inicial: date) -> float:
        """Movimentos anteriores à data inicial (entradas - saídas)."""
        cur.execute(
            """
            SELECT COALESCE(SUM(
                       CASE WHEN tipo = 'E' THEN quantidade
                            ELSE -quantidade END), 0)
              FROM movimentos_kardex
             WHERE produto_id = %s
               AND data_movimento < %s
            """,
            (produto_id, data_inicial),
        )
        return float(cur.fetchone()[0])

    @staticmethod
    def _movimentos(cur, produto_id: int, data_inicial: date,
                    data_final: date) -> list[MovimentoKardex]:
        cur.execute(
            """
            SELECT data_movimento, documento, historico, tipo,
                   quantidade, custo_unitario
              FROM movimentos_kardex
             WHERE produto_id = %s
               AND data_movimento BETWEEN %s AND %s
             ORDER BY data_movimento, id
            """,
            (produto_id, data_inicial, data_final),
        )
        return [
            MovimentoKardex(
                data=l[0].isoformat() if hasattr(l[0], "isoformat")
                else str(l[0]),
                documento=l[1] or "",
                historico=l[2] or "",
                tipo=TIPO_ENTRADA if l[3] == TIPO_ENTRADA else TIPO_SAIDA,
                quantidade=float(l[4]),
                custo_unitario=float(l[5]) if l[5] is not None else None,
            )
            for l in cur.fetchall()
        ]
