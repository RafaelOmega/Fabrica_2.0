# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de kardex do produto."""
from dataclasses import dataclass, field

TIPO_ENTRADA = "E"
TIPO_SAIDA = "S"  # reservado para a futura tela de Saída


@dataclass
class MovimentoKardex:
    data: str                 # ISO AAAA-MM-DD
    documento: str            # sequência da entrada (futuro: doc da saída)
    historico: str            # motivo (futuro: cliente/observação da saída)
    tipo: str = TIPO_ENTRADA  # "E" = entrada | "S" = saída
    quantidade: float = 0.0   # em sacos (entrada já convertida kg → sacos)
    custo_unitario: float | None = None  # custo de aquisição do movimento
    saldo: float = 0.0        # acumulado (preenchido pelo service)

    @property
    def entrada(self) -> float:
        return self.quantidade if self.tipo == TIPO_ENTRADA else 0.0

    @property
    def saida(self) -> float:
        return self.quantidade if self.tipo == TIPO_SAIDA else 0.0


@dataclass
class KardexProduto:
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    unidade: str = "kg"        # unidade de medida do produto (ex: "saco")
    fator_kg_saco: float = 1.0  # kg por saco (conversão das entradas)
    saldo_inicial: float = 0.0  # em sacos
    movimentos: list[MovimentoKardex] = field(default_factory=list)

    @property
    def entradas_total(self) -> float:
        return sum(m.entrada for m in self.movimentos)

    @property
    def saidas_total(self) -> float:
        return sum(m.saida for m in self.movimentos)

    @property
    def saldo_final(self) -> float:
        return self.saldo_inicial + self.entradas_total - self.saidas_total
