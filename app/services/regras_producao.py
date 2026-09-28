# -*- coding: utf-8 -*-
"""Regras de produção: baixa proporcional de insumos pela ficha técnica.

Mesmo padrão de regras_entrada: funções puras consultadas pelo
controller; nada de tela ou banco aqui.
"""

from app.models.entrada import BaixaInsumo
from app.models.ficha_tecnica import FichaTecnica


def ficha_valida(ficha: FichaTecnica | None) -> bool:
    """Ficha utilizável para produzir: existe e tem sacos_batida > 0."""
    return ficha is not None and ficha.sacos_batida > 0


def calcular_baixa(ficha: FichaTecnica,
                   sacos_produzidos: float) -> list[BaixaInsumo]:
    """Kg de cada insumo a baixar, proporcional a sacos_batida.

    proporcao = sacos_produzidos / sacos_batida
    kg_baixa  = quantidade_kg_da_ficha * proporcao  (4 casas)
    """
    if ficha is None or ficha.sacos_batida <= 0:
        raise ValueError("Ficha técnica inválida para produção.")
    if sacos_produzidos <= 0:
        raise ValueError("Sacos produzidos deve ser maior que zero.")
    proporcao = sacos_produzidos / ficha.sacos_batida
    return [
        BaixaInsumo(
            produto_id=item.produto_id,
            codigo_produto=item.codigo_produto,
            quantidade_kg=round(item.quantidade_kg * proporcao, 4),
        )
        for item in ficha.itens
        if item.produto_id is not None
    ]


def custo_producao(baixas: list[BaixaInsumo],
                   custo_por_codigo: dict[str, float]) -> float:
    """Custo do acabado = soma (kg baixado x custo do insumo), 4 casas."""
    return round(sum(
        baixa.quantidade_kg * custo_por_codigo.get(baixa.codigo_produto, 0.0)
        for baixa in baixas
    ), 4)
