# -*- coding: utf-8 -*-
"""Modelos de domínio Ficha Técnica e seus itens."""
from dataclasses import asdict, dataclass, field


@dataclass
class ItemFichaTecnica:
    produto_id: int | None = None
    codigo_produto: str = ""
    quantidade_kg: float = 0.0
    ficha_id: int | None = None
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "ItemFichaTecnica":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            quantidade_kg=float(dados.get("quantidade_kg", 0.0) or 0.0),
            ficha_id=dados.get("ficha_id"),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FichaTecnica:
    produto_id: int | None = None
    codigo_produto: str = ""
    sacos_batida: float = 0.0
    id: int | None = None
    itens: list[ItemFichaTecnica] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dados: dict) -> "FichaTecnica":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            sacos_batida=float(dados.get("sacos_batida", 0.0) or 0.0),
            id=dados.get("id"),
            itens=[ItemFichaTecnica.from_dict(i)
                   for i in dados.get("itens", [])],
        )

    def to_dict(self) -> dict:
        dados = asdict(self)
        return dados
