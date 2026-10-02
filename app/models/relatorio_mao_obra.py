# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de mão de obra."""
from dataclasses import dataclass, field


@dataclass
class LinhaMaoObraSaida:
    """Mão de obra de uma saída específica (detalhe)."""
    saida_id: int | None = None
    sequencia: int | None = None
    data_saida: str = ""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade: float = 0.0
    custo: float = 0.0

    @property
    def total(self) -> float:
        return self.quantidade * self.custo


@dataclass
class ResumoMaoObra:
    """Resumo agregado por mão de obra no período."""
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
    """Relatório de mão de obra: detalhe saída a saída + resumo."""
    data_inicial: str = ""
    data_final: str = ""
    linhas: list[LinhaMaoObraSaida] = field(default_factory=list)
    resumo: list[ResumoMaoObra] = field(default_factory=list)

    @property
    def total_geral(self) -> float:
        return sum(l.total for l in self.linhas)
