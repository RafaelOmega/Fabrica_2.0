# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de mão de obra."""
from dataclasses import dataclass, field


@dataclass
class LinhaMaoObraSaida:
    """Mão de obra de uma saída específica (detalhe)."""
    saida_id: int | None = None
    sequencia: int | None = None
    data_saida: str = ""
    destino: str = ""
    retirada: str = ""
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
    """Relatório de mão de obra: detalhe saída a saída + resumo.

    Com somente_resumo=True, o detalhe não é gerado (linhas vazia)
    e o relatório mostra apenas o resumo agregado.
    """
    data_inicial: str = ""
    data_final: str = ""
    somente_resumo: bool = False
    linhas: list[LinhaMaoObraSaida] = field(default_factory=list)
    resumo: list[ResumoMaoObra] = field(default_factory=list)

    @property
    def tem_dados(self) -> bool:
        return bool(self.linhas or self.resumo)

    @property
    def total_geral(self) -> float:
        if self.linhas:
            return sum(l.total for l in self.linhas)
        return sum(r.total for r in self.resumo)
