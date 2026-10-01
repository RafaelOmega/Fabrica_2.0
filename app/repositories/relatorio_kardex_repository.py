# -*- coding: utf-8 -*-
"""Repositório do relatório de kardex (PostgreSQL).

Fonte: tabela movimentos_kardex (espelho dos movimentos).
Entradas gravam tipo 'E' em kg; as baixas de produção ('S') já entram
em sacos. Para somar tudo na mesma unidade, este repositório converte
as entradas para sacos usando o fator_conversao da unidade de medida
do produto (kg por saco). Se o produto não tiver unidade cadastrada,
mantém kg como fallback (fator = 1).
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
        """Kardex por produto no período (valores em sacos).

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
                        cur, produto, data_inicial)
                    produto.movimentos = self._movimentos(
                        cur, produto, data_inicial, data_final)
        logger.info("Kardex: %s produto(s) no período", len(produtos))
        return produtos

    # ---------------- auxiliares ----------------

    @staticmethod
    def _converte_kg_para_sacos(kg: float, fator: float) -> float:
        """kg -> sacos. Sem fator válido, mantém kg (fallback fator=1)."""
        if fator and fator > 0:
            return kg / fator
        return kg

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
                               COALESCE(um.descricao, 'kg'),
                               COALESCE(um.fator_conversao, 0)
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
                               COALESCE(um.descricao, 'kg'),
                               COALESCE(um.fator_conversao, 0)
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
                        fator_kg_saco=float(l[4] or 0) or 1.0,
                    )
                    for l in cur.fetchall()
                ]

    @staticmethod
    def _saldo_inicial(cur, produto: KardexProduto,
                       data_inicial: date) -> float:
        """Movimentos anteriores à data inicial, tudo convertido a sacos.

        Entradas antigas (kg) são divididas pelo fator; as saídas
        ('S') já estão em sacos.
        """
        cur.execute(
            """
            SELECT COALESCE(SUM(CASE WHEN tipo = 'E' THEN quantidade
                                     ELSE 0 END), 0),
                   COALESCE(SUM(CASE WHEN tipo = 'S' THEN quantidade
                                     ELSE 0 END), 0)
              FROM movimentos_kardex
             WHERE produto_id = %s AND data_movimento < %s
            """,
            (produto.produto_id, data_inicial),
        )
        entradas_kg, saidas_sacos = cur.fetchone()
        fator = produto.fator_kg_saco
        entradas_sacos = (float(entradas_kg) / fator
                          if fator and fator > 0 else 0.0)
        return entradas_sacos - float(saidas_sacos or 0.0)

    @staticmethod
    def _movimentos(cur, produto: KardexProduto, data_inicial: date,
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
            (produto.produto_id, data_inicial, data_final),
        )
        fator = produto.fator_kg_saco
        movimentos = []
        for l in cur.fetchall():
            tipo = TIPO_ENTRADA if l[3] == TIPO_ENTRADA else TIPO_SAIDA
            quantidade = float(l[4])
            # entradas gravam kg -> converte para sacos; saídas já em sacos
            if tipo == TIPO_ENTRADA:
                quantidade = (quantidade / fator
                              if fator and fator > 0 else quantidade)
            movimentos.append(MovimentoKardex(
                data=l[0].isoformat() if hasattr(l[0], "isoformat")
                else str(l[0]),
                documento=l[1] or "",
                historico=l[2] or "",
                tipo=tipo,
                quantidade=quantidade,
                custo_unitario=float(l[5]) if l[5] is not None else None,
            ))
        return movimentos