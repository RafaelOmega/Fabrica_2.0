# -*- coding: utf-8 -*-
"""Regras especiais de produtos na entrada.

Centraliza as regras de negócio por produto para que o controller
apenas consulte e aplique o resultado na tela.
"""

# produto especial: milho a granel (custo = valor da sacaria / 60)
CODIGO_MILHO = "116431"
DIVISOR_MILHO = 60.0


def tem_regra_especial(codigo: str) -> bool:
    """Indica se o produto tem regra especial de entrada."""
    return codigo == CODIGO_MILHO


def calcular_custo(codigo: str,
                   valor_milho: float | None = None) -> float | None:
    """Calcula o custo do item conforme a regra do produto.

    Retorna None quando não há regra especial ou o valor é inválido
    (nesse caso o custo vem do campo/cadastro pelo controller).
    """
    if codigo != CODIGO_MILHO:
        return None
    if valor_milho is None or valor_milho <= 0:
        return None
    return valor_milho / DIVISOR_MILHO
