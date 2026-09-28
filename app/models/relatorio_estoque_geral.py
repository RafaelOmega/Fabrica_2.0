# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de estoque geral."""
from dataclasses import dataclass


@dataclass
class LinhaEstoqueGeral:
    """Uma linha do relatório: posição de estoque de um produto."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    entradas: float = 0.0        # no período (data inicial a final)
    saidas: float = 0.0          # no período (data inicial a final)
    saldo: float = 0.0           # posição até a data final
    custo_unitario: float = 0.0  # custo cadastrado do produto

    @property
    def valor_estoque(self) -> float:
        return round(self.saldo * self.custo_unitario, 4)
