# -*- coding: utf-8 -*-
"""Regras de produção: baixa proporcional de insumos pela ficha técnica.

Mesmo padrão de regras_entrada: funções puras consultadas pelo
controller; nada de tela ou banco aqui.

A quantidade é convertida para sacos usando o fator_conversao da
unidade de medida do insumo (kg por saco). Se o insumo não tiver
unidade/fator, mantém o valor em kg como fallback (fator = 1).
"""
from app.models.entrada import BaixaInsumo
from app.models.ficha_tecnica import FichaTecnica


def ficha_valida(ficha: FichaTecnica | None) -> bool:
    """Ficha utilizável para produzir: existe e tem sacos_batida > 0."""
    return ficha is not None and ficha.sacos_batida > 0


def calcular_baixa(ficha: FichaTecnica,
                   sacos_produzidos: float) -> list[BaixaInsumo]:
    """Baixa de cada insumo, proporcional a sacos_batida.

    proporcao = sacos_produzidos / sacos_batida
    kg_baixa  = quantidade_kg_da_ficha * proporcao       (4 casas)
    sacos     = kg_baixa / fator_conversao_kg_saco        (4 casas)
    """
    if ficha is None or ficha.sacos_batida <= 0:
        raise ValueError("Ficha técnica inválida para produção.")
    if sacos_produzidos <= 0:
        raise ValueError("Sacos produzidos deve ser maior que zero.")
    proporcao = sacos_produzidos / ficha.sacos_batida
    baixas = []
    for item in ficha.itens:
        if item.produto_id is None:
            continue
        kg_baixa = round(item.quantidade_kg * proporcao, 4)
        fator = item.fator_conversao_kg_saco
        # converte p/ sacos; sem fator cadastrado, mantém kg (fallback)
        sacos = (round(kg_baixa / fator, 4)
                 if fator and fator > 0 else kg_baixa)
        baixas.append(BaixaInsumo(
            produto_id=item.produto_id,
            codigo_produto=item.codigo_produto,
            quantidade_kg=kg_baixa,
            quantidade_sacos=sacos,
            fator_conversao=fator,
        ))
    return baixas


def custo_producao(baixas: list[BaixaInsumo],
                   custo_por_codigo: dict[str, float]) -> float:
    """Custo do acabado = soma (kg baixado x custo do insumo), 4 casas."""
    return round(sum(
        baixa.quantidade_kg * custo_por_codigo.get(baixa.codigo_produto, 0.0)
        for baixa in baixas
    ), 4)
