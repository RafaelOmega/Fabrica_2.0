# -*- coding: utf-8 -*-
"""Repositório do relatório de baixa de ficha técnica (PostgreSQL).

Fonte: entradas de produção (motivo com baixa_producao=true).
  - itens_entrada                          -> produtos acabados produzidos
  - fichas_tecnicas / itens_ficha_tecnica  -> o que compõe cada acabado
A quantidade de cada insumo é proporcional à quantidade produzida
(sacos_batida da ficha), convertida pelo fator da unidade de medida.
A origem da baixa é a própria entrada de produção.
"""
from datetime import date

from app.database import get_connection
from app.models.relatorio_baixa_ficha_tecnica import (
    EntradaBaixa, GrupoAcabado, ItemComposicao, ProducaoAcabado,
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
        """Baixas de ficha técnica do período.

        Monta as duas visões: por entrada (todas) e por produto acabado
        (filtrável por ficha_produto_id).
        """
        relatorio = RelatorioBaixaFichaTecnica(
            data_inicial=data_inicial.isoformat(),
            data_final=data_final.isoformat(),
            ficha_produto_id=ficha_produto_id,
        )
        with self._conn:
            with self._conn.cursor() as cur:
                # 1) entradas de produção do período
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
                entradas = cur.fetchall()
                if not entradas:
                    return relatorio
                ids_entradas = [l[0] for l in entradas]
                dados_entradas = {l[0]: l for l in entradas}

                # 2) acabados produzidos em cada entrada
                cur.execute(
                    """
                    SELECT ie.entrada_id, ie.produto_id, p.codigo,
                           p.descricao, ie.quantidade, ie.custo
                      FROM itens_entrada ie
                      LEFT JOIN produtos p ON p.id = ie.produto_id
                     WHERE ie.entrada_id = ANY(%s)
                       AND ie.produto_id IS NOT NULL
                     ORDER BY ie.entrada_id, ie.id
                    """,
                    (ids_entradas,),
                )
                acabados = cur.fetchall()
                if not acabados:
                    return relatorio
                ids_acabados = sorted({l[1] for l in acabados})

                # 3) ficha técnica mais recente de cada acabado
                cur.execute(
                    """
                    SELECT f.produto_id, f.id, f.sacos_batida
                      FROM fichas_tecnicas f
                      JOIN (SELECT produto_id, MAX(id) AS id
                              FROM fichas_tecnicas GROUP BY produto_id) g
                        ON g.id = f.id
                     WHERE f.produto_id = ANY(%s)
                    """,
                    (ids_acabados,),
                )
                ficha_por_produto = {}
                for produto_id, ficha_id, sacos in cur.fetchall():
                    ficha_por_produto[produto_id] = (ficha_id,
                                                     float(sacos or 0))

                # 4) itens das fichas (insumos + custo + fator + estoque)
                ids_fichas = [v[0] for v in ficha_por_produto.values()]
                itens_por_ficha = {}
                if ids_fichas:
                    cur.execute(
                        """
                        SELECT fi.ficha_id, fi.produto_id, p.codigo,
                               p.descricao, fi.quantidade_kg,
                               COALESCE(p.custo, 0),
                               COALESCE(um.fator_conversao, 0),
                               COALESCE(p.controla_estoque, TRUE)
                          FROM itens_ficha_tecnica fi
                          LEFT JOIN produtos p ON p.id = fi.produto_id
                          LEFT JOIN unidades_medida um
                                 ON um.codigo = p.unidade
                         WHERE fi.ficha_id = ANY(%s)
                        """,
                        (ids_fichas,),
                    )
                    for l in cur.fetchall():
                        itens_por_ficha.setdefault(l[0], []).append(l[1:])

        # 5) monta as produções (um acabado por entrada, com os itens)
        producoes: list[ProducaoAcabado] = []
        for (entrada_id, produto_id, codigo, descricao,
             quantidade, custo) in acabados:
            producao = ProducaoAcabado(
                produto_id=produto_id,
                codigo=codigo or "",
                descricao=descricao or "",
                quantidade=float(quantidade or 0),
                custo_acabado=float(custo or 0),
                entrada_id=entrada_id,
                sequencia=dados_entradas[entrada_id][1],
                data_entrada=(dados_entradas[entrada_id][2].isoformat()
                              if hasattr(dados_entradas[entrada_id][2],
                                         "isoformat")
                              else str(dados_entradas[entrada_id][2] or "")),
            )
            ficha = ficha_por_produto.get(produto_id)
            if ficha and ficha[1] > 0:
                ficha_id, sacos_batida = ficha
                proporcao = producao.quantidade / sacos_batida
                for (insumo_id, insumo_codigo, insumo_descricao,
                     quantidade_kg, custo_insumo, fator,
                     controla_estoque) in itens_por_ficha.get(ficha_id, []):
                    if not controla_estoque or insumo_id is None:
                        continue
                    kg = round(float(quantidade_kg or 0) * proporcao, 4)
                    sacos = (round(kg / float(fator), 4)
                             if fator and float(fator) > 0 else kg)
                    producao.itens.append(ItemComposicao(
                        produto_id=insumo_id,
                        codigo=insumo_codigo or "",
                        descricao=insumo_descricao or "",
                        quantidade_sacos=sacos,
                        custo=float(custo_insumo or 0),
                        origem_entrada_id=entrada_id,
                        origem_sequencia=producao.sequencia,
                        origem_data=producao.data_entrada,
                    ))
            producoes.append(producao)

        # 6) visão por entrada (sempre)
        por_entrada: dict[int, list[ProducaoAcabado]] = {}
        for p in producoes:
            por_entrada.setdefault(p.entrada_id, []).append(p)
        for entrada_id, l in dados_entradas.items():
            relatorio.entradas.append(EntradaBaixa(
                entrada_id=entrada_id,
                sequencia=l[1],
                data_entrada=(l[2].isoformat()
                              if hasattr(l[2], "isoformat")
                              else str(l[2] or "")),
                motivo_descricao=l[3] or "",
                acabados=por_entrada.get(entrada_id, []),
            ))

        # 7) visão por produto acabado (modo filtrado)
        por_produto: dict[int, list[ProducaoAcabado]] = {}
        for p in producoes:
            por_produto.setdefault(p.produto_id, []).append(p)
        for produto_id, lista in por_produto.items():
            ref = lista[0]
            relatorio.grupos.append(GrupoAcabado(
                produto_id=produto_id,
                codigo=ref.codigo,
                descricao=ref.descricao,
                producoes=lista,
            ))
        relatorio.grupos.sort(key=lambda g: (g.codigo, g.descricao))

        logger.info("Relatório de baixa gerado: %s entradas, %s grupos",
                    len(relatorio.entradas), len(relatorio.grupos))
        return relatorio
