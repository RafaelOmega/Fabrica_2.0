# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de mão de obra."""
from dataclasses import dataclass, field


@dataclass
class LinhaMaoObra:
    """Uma linha do relatório: mão de obra consumida nas saídas do período."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade: float = 0.0
    custo: float = 0.0

    @property
    def total(self) -> float:
        return self.quantidade * self.custo


@dataclass
class RelatorioMaoObra:
    """Relatório agregado por mão de obra no período."""
    data_inicial: str = ""
    data_final: str = ""
    linhas: list[LinhaMaoObra] = field(default_factory=list)

    @property
    def total_geral(self) -> float:
        return sum(l.total for l in self.linhas)
