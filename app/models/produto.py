# -*- coding: utf-8 -*-
"""Modelo de domínio Produto."""
from dataclasses import asdict, dataclass


@dataclass
class Produto:
    codigo: str
    descricao: str
    unidade: str = ""  # código da unidade de medida (FK unidades_medida)
    unidade_descricao: str = ""  # apenas exibição (vem do JOIN com unidades)
    peso: float = 0.0
    custo: float = 0.0
    mat_prima: bool = False
    prod_acabado: bool = False
    mao_obra: bool = False
    controla_estoque: bool = False
    embalagem: bool = False
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "Produto":
        return cls(
            codigo=str(dados.get("codigo", "")),
            descricao=str(dados.get("descricao", "")),
            unidade=str(dados.get("unidade", "")),
            unidade_descricao=str(dados.get("unidade_descricao", "")),
            peso=float(dados.get("peso", 0.0) or 0.0),
            custo=float(dados.get("custo", 0.0) or 0.0),
            mat_prima=bool(dados.get("mat_prima", False)),
            prod_acabado=bool(dados.get("prod_acabado", False)),
            mao_obra=bool(dados.get("mao_obra", False)),
            controla_estoque=bool(dados.get("controla_estoque", False)),
            embalagem=bool(dados.get("embalagem", False)),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)
