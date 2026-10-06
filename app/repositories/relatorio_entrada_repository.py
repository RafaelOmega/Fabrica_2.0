# -*- coding: utf-8 -*-
"""Repositório do relatório de entradas (PostgreSQL).

Fonte: entradas + itens_entrada (descrição via JOIN com produtos).
Filtros:
  - entrada específica (id vindo da pesquisa)
  - produto (id vindo da pesquisa) com dois modos:
      * entrada completa: entradas que contêm o produto, com TODOS os itens
      * só o produto: mesmas entradas, apenas os itens do produto
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
                  entrada_id: int | None = None,
                  produto_id: int | None = None,
                  so_produto: bool = False) -> RelatorioEntrada:
        """Entradas do período (ou específica), com seus itens.

        Com produto_id: só entradas que contêm o produto; em
        so_produto=True os itens ficam restritos ao produto.
        """
        relatorio = RelatorioEntrada(
            data_inicial=data_inicial.isoformat(),
            data_final=data_final.isoformat(),
            entrada_id=entrada_id,
            produto_id=produto_id,
            so_produto=so_produto,
        )
        with self._conn:
            with self._conn.cursor() as cur:
                # 1) entradas (período ou específica) + filtro de produto
                sql = (
                    "SELECT e.id, e.sequencia, e.data_entrada, "
                    "COALESCE(m.descricao, '') "
                    "FROM entradas e "
                    "LEFT JOIN motivos_entrada m "
                    "ON m.id = e.motivo_entrada_id WHERE "
                )
                params: list = []
                if entrada_id:
                    sql += "e.id = %s"
                    params.append(entrada_id)
                else:
                    sql += "e.data_entrada BETWEEN %s AND %s"
                    params += [data_inicial, data_final]
                if produto_id:
                    sql += (" AND EXISTS (SELECT 1 FROM itens_entrada ie "
                            "WHERE ie.entrada_id = e.id "
                            "AND ie.produto_id = %s)")
                    params.append(produto_id)
                sql += " ORDER BY e.sequencia"
                cur.execute(sql, params)
                entradas = cur.fetchall()
                if not entradas:
                    return relatorio
                ids = [l[0] for l in entradas]

                # 2) itens (restritos ao produto no modo só o produto)
                if produto_id and so_produto:
                    cur.execute(
                        """
                        SELECT ie.entrada_id, ie.produto_id, p.codigo,
                               p.descricao, ie.quantidade, ie.custo
                          FROM itens_entrada ie
                          LEFT JOIN produtos p ON p.id = ie.produto_id
                         WHERE ie.entrada_id = ANY(%s)
                           AND ie.produto_id = %s
                         ORDER BY ie.entrada_id, ie.id
                        """,
                        (ids, produto_id),
                    )
                else:
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
        logger.info("Relatório de entradas gerado: %s entradas "
                    "(produto=%s, só produto=%s)",
                    len(relatorio.linhas), produto_id, so_produto)
        return relatorio
