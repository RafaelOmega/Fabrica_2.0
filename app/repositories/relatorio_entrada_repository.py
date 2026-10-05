# -*- coding: utf-8 -*-
"""Repositório do relatório de entradas (PostgreSQL).

Fonte: entradas + itens_entrada (descrição via JOIN com produtos).
Filtro opcional por entrada específica (id vindo da pesquisa).
"""
from datetime import date

from app.database import get_connection
from app.models.relatorio_entrada import (
    ItemRelatorioEntrada, LinhaEntrada, RelatorioEntrada,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_entrada")


class RelatorioEntradaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def relatorio(self, data_inicial: date, data_final: date,
                  entrada_id: int | None = None) -> RelatorioEntrada:
        """Entradas do período (ou uma específica), com seus itens."""
        relatorio = RelatorioEntrada(
            data_inicial=data_inicial.isoformat(),
            data_final=data_final.isoformat(),
            entrada_id=entrada_id,
        )
        with self._conn:
            with self._conn.cursor() as cur:
                # 1) entradas do período (ou a selecionada)
                if entrada_id:
                    cur.execute(
                        """
                        SELECT e.id, e.sequencia, e.data_entrada,
                               COALESCE(m.descricao, '')
                          FROM entradas e
                          LEFT JOIN motivos_entrada m
                                 ON m.id = e.motivo_entrada_id
                         WHERE e.id = %s
                         ORDER BY e.sequencia
                        """,
                        (entrada_id,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT e.id, e.sequencia, e.data_entrada,
                               COALESCE(m.descricao, '')
                          FROM entradas e
                          LEFT JOIN motivos_entrada m
                                 ON m.id = e.motivo_entrada_id
                         WHERE e.data_entrada BETWEEN %s AND %s
                         ORDER BY e.sequencia
                        """,
                        (data_inicial, data_final),
                    )
                entradas = cur.fetchall()
                if not entradas:
                    return relatorio
                ids = [l[0] for l in entradas]

                # 2) itens das entradas (descrição pronta do JOIN)
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
                itens_por_entrada: dict[int, list[ItemRelatorioEntrada]] = {}
                for l in cur.fetchall():
                    itens_por_entrada.setdefault(l[0], []).append(
                        ItemRelatorioEntrada(
                            produto_id=l[1],
                            codigo=l[2] or "",
                            descricao=l[3] or "",
                            quantidade=float(l[4] or 0),
                            custo=float(l[5] or 0),
                        ))

        for entrada_id_, sequencia, data_entrada, motivo in entradas:
            relatorio.linhas.append(LinhaEntrada(
                entrada_id=entrada_id_,
                sequencia=sequencia,
                data_entrada=(data_entrada.isoformat()
                              if hasattr(data_entrada, "isoformat")
                              else str(data_entrada or "")),
                motivo_descricao=motivo or "",
                itens=itens_por_entrada.get(entrada_id_, []),
            ))
        logger.info("Relatório de entradas gerado: %s entradas",
                    len(relatorio.linhas))
        return relatorio
