# -*- coding: utf-8 -*-
"""Modelo de domínio: registro de alteração de custo de produto."""
from dataclasses import asdict, dataclass


@dataclass
class AlteracaoCusto:
    produto_id: int
    custo_anterior: float
    custo_novo: float
    origem: str = "entrada"
    entrada_id: int | None = None
    id: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)
