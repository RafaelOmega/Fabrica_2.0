# -*- coding: utf-8 -*-
"""Repositório do relatório de baixa de ficha técnica (PostgreSQL).

Fonte: entradas de produção (motivo com baixa_producao=true).
  - itens_entrada      -> produtos acabados da entrada
  - movimentos_kardex  -> baixas dos insumos (tipo 'S' com entrada_id)
A baixa não fica em tabela própria: é gravada no kardex no salvar da
entrada, então o relatório lê o kardex (fiel ao que foi lançado).
"""
from datetime import date

from app.database import get_connection
from app.models.relatorio_baixa_ficha_tecnica import (
    AcabadoBaixa, BaixaFichaTecnica, ItemBaixaFicha,
    RelatorioBaixaFichaTecnica,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_baixa_ficha_tecnica")


class RelatorioBaixaFichaTecnicaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def relatorio(self, data_inicial: date, data_final: date,
                  ficha_produto_id: int | None = None
                  ) -> RelatorioBaixaFichaTecnica:
        """Baixas de ficha técnica do período, entrada a entrada.

        Se ficha_produto_id informado, traz só as entradas que contêm
        aquele produto acabado.
        """
        relatorio = RelatorioBaixaFichaTecnica(
            data_inicial=data_inicial.isoformat(),
            data_final=data_final.isoformat(),
        )
        with self._conn:
            with self._conn.cursor() as cur:
                # entradas de produção do período
                if ficha_produto_id:
                    cur.execute(
                        """
                        SELECT e.id, e.sequencia, e.data_entrada,
                               COALESCE(m.descricao, '')
                          FROM entradas e
                          JOIN motivos_entrada m ON m.id = e.motivo_entrada_id
                         WHERE m.baixa_producao = TRUE
                           AND e.data_entrada BETWEEN %s AND %s
                           AND EXISTS (
                                SELECT 1 FROM itens_entrada ie
                                 WHERE ie.entrada_id = e.id
                                   AND ie.produto_id = %s)
                         ORDER BY e.sequencia
                        """,
                        (data_inicial, data_final, ficha_produto_id),
                    )
                else:
                    cur.execute(
                        """
                        SELECT e.id, e.sequencia, e.data_entrada,
                               COALESCE(m.descricao, '')
                          FROM entradas e
                          JOIN motivos_entrada m ON m.id = e.motivo_entrada_id
                         WHERE m.baixa_producao = TRUE
                           AND e.data_entrada BETWEEN %s AND %s
                         ORDER BY e.sequencia
                        """,
                        (data_inicial, data_final),
                    )
                linhas = cur.fetchall()
                if not linhas:
                    return relatorio

                ids = [l[0] for l in linhas]
                sequencia_por_id = {l[0]: l for l in linhas}

                # acabados da entrada (itens_entrada)
                cur.execute(
                    """
                    SELECT ie.entrada_id, ie.produto_id, p.codigo,
                           p.descricao, ie.quantidade, ie.custo
                      FROM itens_entrada ie
                      LEFT JOIN produtos p ON p.id = ie.produto_id
                     WHERE ie.entrada_id = ANY(%s)
                     ORDER BY ie.entrada_id, ie.id
                    """,
                    (ids,),
                )
                acabados_por_entrada: dict[int, list[AcabadoBaixa]] = {}
                for l in cur.fetchall():
                    acabados_por_entrada.setdefault(l[0], []).append(
                        AcabadoBaixa(
                            produto_id=l[1],
                            codigo=l[2] or "",
                            descricao=l[3] or "",
                            quantidade=float(l[4] or 0),
                            custo=float(l[5] or 0),
                        ))

                # baixas dos insumos (kardex tipo 'S' com entrada_id)
                cur.execute(
                    """
                    SELECT m.entrada_id, m.produto_id, p.codigo,
                           p.descricao, m.quantidade, m.custo_unitario
                      FROM movimentos_kardex m
                      LEFT JOIN produtos p ON p.id = m.produto_id
                     WHERE m.tipo = 'S'
                       AND m.entrada_id = ANY(%s)
                     ORDER BY m.entrada_id, m.id
                    """,
                    (ids,),
                )
                itens_por_entrada: dict[int, list[ItemBaixaFicha]] = {}
                for l in cur.fetchall():
                    itens_por_entrada.setdefault(l[0], []).append(
                        ItemBaixaFicha(
                            produto_id=l[1],
                            codigo=l[2] or "",
                            descricao=l[3] or "",
                            quantidade=float(l[4] or 0),
                            custo=float(l[5] or 0),
                        ))

        for entrada_id, l in sequencia_por_id.items():
            relatorio.linhas.append(BaixaFichaTecnica(
                entrada_id=entrada_id,
                sequencia=l[1],
                data_entrada=(l[2].isoformat()
                              if hasattr(l[2], "isoformat")
                              else str(l[2] or "")),
                motivo_descricao=l[3] or "",
                acabados=acabados_por_entrada.get(entrada_id, []),
                itens=itens_por_entrada.get(entrada_id, []),
            ))
        return relatorio
