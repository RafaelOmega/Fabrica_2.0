# -*- coding: utf-8 -*-
"""Regras especiais de produtos na entrada.

Centraliza as regras de negócio por produto para que o controller
apenas consulte e aplique o resultado na tela.
"""

# produto especial: milho a granel (custo = valor da sacaria / 60)
CODIGO_MILHO = "116431"
DIVISOR_MILHO = 60.0

# motivo que habilita a regra do milho: identificado pelo TEXTO do
# cadastro de motivos de entrada (independe do código numérico)
MOTIVO_COMPRA = "compra"

TOLERANCIA_CUSTO = 0.00001


def _motivo_e_compra(motivo_descricao: str) -> bool:
    """Compara o texto do motivo com 'Compra' (ignora caixa/espacos)."""
    return motivo_descricao.strip().casefold() == MOTIVO_COMPRA


def tem_regra_especial(codigo: str, motivo_descricao: str = "") -> bool:
    """Indica se o produto tem regra especial de entrada.

    A regra do milho vale apenas quando o motivo for Compra.
    """
    return (codigo == CODIGO_MILHO
            and _motivo_e_compra(motivo_descricao))


def calcular_custo(codigo: str, valor_milho: float | None = None,
                   motivo_descricao: str = "") -> float | None:
    """Calcula o custo do item conforme a regra do produto.
Retorna None quando não há regra especial ou o valor é inválido
    (nesse caso o custo vem do campo/cadastro pelo controller).
    """
    if not tem_regra_especial(codigo, motivo_descricao):
        return None
    if valor_milho is None or valor_milho <= 0:
        return None
    return valor_milho / DIVISOR_MILHO


def custo_diverge(custo_cadastrado: float, custo_item: float) -> bool:
    """Indica se o custo do item difere do custo cadastrado do produto."""
    return abs(custo_cadastrado - custo_item) > TOLERANCIA_CUSTO
