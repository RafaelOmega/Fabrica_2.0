# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de fichas técnicas."""
from dataclasses import dataclass, field


@dataclass
class InsumoRelatorio:
    codigo_produto: str = ""
    descricao: str = ""
    quantidade_kg: float = 0.0
    custo_saco: float | None = None  # custo cadastrado do produto
    peso_saco: float = 0.0           # peso do produto (cadastro)

    @property
    def custo_kg(self) -> float | None:
        """Custo por kg do insumo (custo cadastrado / peso do produto)."""
        if self.custo_saco is None or self.peso_saco <= 0:
            return None
        return self.custo_saco / self.peso_saco

    @property
    def custo_batida(self) -> float | None:
        """Custo do insumo na batida (kg da batida x custo/kg)."""
        if self.custo_kg is None:
            return None
        return self.quantidade_kg * self.custo_kg


@dataclass
class FichaTecnicaRelatorio:
    id: int | None = None
    codigo_produto: str = ""
    descricao_produto: str = ""
    sacos_batida: float = 0.0
    peso_produto: float = 0.0  # peso do saco do produto acabado (cadastro)
    itens: list[InsumoRelatorio] = field(default_factory=list)

    @property
    def custo_batida(self) -> float:
        """Custo total da batida (soma do custo de cada insumo)."""
        total = 0.0
        for item in self.itens:
            if item.custo_batida is not None:
                total += item.custo_batida
        return total

    @property
    def total_batida_kg(self) -> float | None:
        """kg teóricos da batida (sacos produzidos x peso do saco acabado)."""
        if self.peso_produto <= 0:
            return None
        return self.sacos_batida * self.peso_produto

    def qtde_unitaria(self, item: InsumoRelatorio) -> float | None:
        """kg do insumo por saco produzido (kg na batida / sacos)."""
        if self.sacos_batida <= 0:
            return None
        return item.quantidade_kg / self.sacos_batida

    def custo_unitario(self, item: InsumoRelatorio) -> float | None:
        """Custo do insumo por saco produzido."""
        qtde = self.qtde_unitaria(item)
        if qtde is None or item.custo_kg is None:
            return None
        return qtde * item.custo_kg

    @property
    def custo_unitario_total(self) -> float | None:
        """Custo por saco produzido (custo da batida / sacos por batida)."""
        if self.sacos_batida <= 0:
            return None
        return self.custo_batida / self.sacos_batida
