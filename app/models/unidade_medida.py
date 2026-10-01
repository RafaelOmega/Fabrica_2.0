# -*- coding: utf-8 -*-
"""Modelo de domínio Unidade de Medida."""
from dataclasses import asdict, dataclass


@dataclass
class UnidadeMedida:
    codigo: str = ""
    descricao: str = ""
    fator_conversao: float = 0.0
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "UnidadeMedida":
        return cls(
            codigo=str(dados.get("codigo", "")),
            descricao=str(dados.get("descricao", "")),
            fator_conversao=float(dados.get("fator_conversao", 0.0) or 0.0),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)
