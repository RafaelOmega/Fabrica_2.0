# -*- coding: utf-8 -*-
"""Modelo de domínio Produto."""
from dataclasses import asdict, dataclass


@dataclass
class Produto:
    codigo: str
    descricao: str
    peso: float = 0.0
    custo: float = 0.0
    materia_prima: bool = False
    produto_acabado: bool = False
    mao_obra: bool = False
    controla_estoque: bool = False

    @classmethod
    def from_dict(cls, dados: dict) -> "Produto":
        return cls(
            codigo=str(dados.get("codigo", "")),
            descricao=str(dados.get("descricao", "")),
            peso=float(dados.get("peso", 0.0) or 0.0),
            custo=float(dados.get("custo", 0.0) or 0.0),
            materia_prima=bool(dados.get("materia_prima", False)),
            produto_acabado=bool(dados.get("produto_acabado", False)),
            mao_obra=bool(dados.get("mao_obra", False)),
            controla_estoque=bool(dados.get("controla_estoque", False)),
        )

    def to_dict(self) -> dict:
        return asdict(self)
