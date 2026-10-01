# -*- coding: utf-8 -*-
"""Repositório do relatório de mão de obra (PostgreSQL).

Fonte: tabela itens_saida_mao_obra (mão de obra das saídas),
vinculada às saídas pelo saida_id. A mão de obra não controla estoque,
por isso não vem do kardex.
"""
from datetime import date

from app.database import get_connection
from app.models.relatorio_mao_obra import LinhaMaoObra, RelatorioMaoObra
from app.utils.logger import get_logger

logger = get_logger("relatorio_mao_obra")


class RelatorioMaoObraRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def relatorio(self, data_inicial: date, data_final: date,
                  produto_id: int | None = None) -> RelatorioMaoObra:
        """Mão de obra das saídas no período, agregada por produto.

        Se produto_id informado, filtra só a mão de obra daquele produto.
        """
        with self._conn:
            with self._conn.cursor() as cur:
                if produto_id:
                    cur.execute(
                        """
                        SELECT m.produto_id, p.codigo, p.descricao,
                               COALESCE(SUM(m.quantidade), 0),
                               COALESCE(SUM(m.quantidade * m.custo), 0)
                          FROM itens_saida_mao_obra m
                          JOIN saidas s ON s.id = m.saida_id
                          LEFT JOIN produtos p ON p.id = m.produto_id
                         WHERE s.data_saida BETWEEN %s AND %s
                           AND m.produto_id = %s
                         GROUP BY m.produto_id, p.codigo, p.descricao
                         ORDER BY p.descricao
                        """,
                        (data_inicial, data_final, produto_id),
                    )
                else:
                    cur.execute(
                        """
                        SELECT m.produto_id, p.codigo, p.descricao,
                               COALESCE(SUM(m.quantidade), 0),
                               COALESCE(SUM(m.quantidade * m.custo), 0)
                          FROM itens_saida_mao_obra m
                          JOIN saidas s ON s.id = m.saida_id
                          LEFT JOIN produtos p ON p.id = m.produto_id
                         WHERE s.data_saida BETWEEN %s AND %s
                         GROUP BY m.produto_id, p.codigo, p.descricao
                         ORDER BY p.descricao
                        """,
                        (data_inicial, data_final),
                    )
                linhas = cur.fetchall()
        relatorio = RelatorioMaoObra(
            data_inicial=data_inicial.isoformat(),
            data_final=data_final.isoformat(),
        )
        for l in linhas:
            quantidade = float(l[3] or 0)
            total = float(l[4] or 0)
            custo = (total / quantidade) if quantidade else 0.0
            relatorio.linhas.append(LinhaMaoObra(
                produto_id=l[0],
                codigo=l[1] or "",
                descricao=l[2] or "",
                quantidade=quantidade,
                custo=custo,
            ))
        return relatorio
