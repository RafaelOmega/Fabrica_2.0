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


@dataclass
class FichaTecnicaRelatorio:
    id: int | None = None
    codigo_produto: str = ""
    descricao_produto: str = ""
    sacos_batida: float = 0.0
    itens: list[InsumoRelatorio] = field(default_factory=list)

    @property
    def custo_batida(self) -> float:
        """Custo dos insumos da batida (kg x custo/kg).

        NOTA: considera quantidade_kg como total da batida.
        Se a semântica for 'por saco', multiplicar por sacos_batida.
        """
        total = 0.0
        for item in self.itens:
            if item.custo_kg is not None:
                total += item.quantidade_kg * item.custo_kg
        return total
