# -*- coding: utf-8 -*-
"""Modelos de domínio Ficha Técnica e seus itens."""
from dataclasses import asdict, dataclass, field


@dataclass
class ItemFichaTecnica:
    produto_id: int | None = None
    codigo_produto: str = ""
    quantidade_kg: float = 0.0
    fator_conversao_kg_saco: float = 0.0  # kg por saco (uni. de medida)
    controla_estoque: bool = True         # só baixa insumo que controla estoque
    ficha_id: int | None = None
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "ItemFichaTecnica":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            quantidade_kg=float(dados.get("quantidade_kg", 0.0) or 0.0),
            fator_conversao_kg_saco=float(
                dados.get("fator_conversao_kg_saco", 0.0) or 0.0),
            controla_estoque=bool(dados.get("controla_estoque", True)),
            ficha_id=dados.get("ficha_id"),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FichaTecnica:
    produto_id: int | None = None
    codigo_produto: str = ""
    descricao_produto: str = ""
    sacos_batida: float = 0.0
    id: int | None = None
    itens: list[ItemFichaTecnica] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dados: dict) -> "FichaTecnica":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            descricao_produto=str(dados.get("descricao_produto", "")),
            sacos_batida=float(dados.get("sacos_batida", 0.0) or 0.0),
            id=dados.get("id"),
            itens=[ItemFichaTecnica.from_dict(i)
                   for i in dados.get("itens", [])],
        )

    def to_dict(self) -> dict:
        return asdict(self)
