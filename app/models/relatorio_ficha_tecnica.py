# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de fichas técnicas."""
from dataclasses import dataclass, field


@dataclass
class InsumoRelatorio:
    codigo_produto: str = ""
    descricao: str = ""
    quantidade_kg: float = 0.0
    custo_unitario: float | None = None


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
            if item.custo_unitario is not None:
                total += item.quantidade_kg * item.custo_unitario
        return total
