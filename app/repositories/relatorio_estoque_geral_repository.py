# -*- coding: utf-8 -*-
"""Repositório do relatório de estoque geral (PostgreSQL).

Fonte: tabela movimentos_kardex (espelho dos movimentos).
  - Entradas/Saídas: somas no período (data inicial a data final)
  - Saldo: entradas - saídas até a data final (posição)
  - Custo unitário: custo cadastrado do produto
"""
from app.database import get_connection
from app.models.relatorio_estoque_geral import LinhaEstoqueGeral
from app.utils.logger import get_logger

logger = get_logger("relatorio_estoque_geral_repository")

_SQL = """
    SELECT p.id, p.codigo, p.descricao,
           COALESCE(e.total, 0),
           COALESCE(s.total, 0),
           COALESCE(pos.total, 0),
           p.custo
      FROM produtos p
      LEFT JOIN (
            SELECT produto_id, SUM(quantidade) AS total
              FROM movimentos_kardex
             WHERE tipo = 'E'
               AND data_movimento BETWEEN %s AND %s
             GROUP BY produto_id
           ) e ON e.produto_id = p.id
      LEFT JOIN (
            SELECT produto_id, SUM(quantidade) AS total
              FROM movimentos_kardex
             WHERE tipo = 'S'
               AND data_movimento BETWEEN %s AND %s
             GROUP BY produto_id
           ) s ON s.produto_id = p.id
      LEFT JOIN (
            SELECT produto_id,
                   SUM(CASE WHEN tipo = 'E' THEN quantidade
                            ELSE -quantidade END) AS total
              FROM movimentos_kardex
             WHERE data_movimento <= %s
             GROUP BY produto_id
           ) pos ON pos.produto_id = p.id
     WHERE EXISTS (
            SELECT 1
              FROM movimentos_kardex mk
             WHERE mk.produto_id = p.id
               AND mk.data_movimento <= %s)
       AND (%s IS NULL OR p.id = %s)
     ORDER BY p.descricao
"""


class RelatorioEstoqueGeralRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def estoque(self, produto_id: int | None, data_inicial: str,
                data_final: str) -> list[LinhaEstoqueGeral]:
        """Linhas do relatório (uma por produto com movimentação).

        produto_id: filtra um único produto (None = todos).
        Datas no formato ISO AAAA-MM-DD.
        """
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    _SQL,
                    (data_inicial, data_final,
                     data_inicial, data_final,
                     data_final, data_final,
                     produto_id, produto_id),
                )
                linhas_bd = cur.fetchall()
        return [
            LinhaEstoqueGeral(
                produto_id=l[0],
                codigo=l[1] or "",
                descricao=l[2] or "",
                entradas=float(l[3]),
                saidas=float(l[4]),
                saldo=float(l[5]),
                custo_unitario=float(l[6] or 0.0),
            )
            for l in linhas_bd
        ]
