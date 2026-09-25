# -*- coding: utf-8 -*-
"""Modelo de domínio Motivo de Entrada."""
from dataclasses import asdict, dataclass


@dataclass
class MotivoEntrada:
    codigo: str
    descricao: str
    baixa_producao: bool = False
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "MotivoEntrada":
        return cls(
            codigo=str(dados.get("codigo", "")),
            descricao=str(dados.get("descricao", "")),
            baixa_producao=bool(dados.get("baixa_producao", False)),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)
