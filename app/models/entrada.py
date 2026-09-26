# -*- coding: utf-8 -*-
"""Modelos de domínio Entrada e seus itens."""
from dataclasses import asdict, dataclass, field


@dataclass
class ItemEntrada:
    produto_id: int | None = None
    codigo_produto: str = ""  # apenas exibição (vem do JOIN com produtos)
    quantidade: float = 0.0
    custo: float = 0.0
    entrada_id: int | None = None
    id: int | None = None

    @property
    def total(self) -> float:
        return self.quantidade * self.custo

    @classmethod
    def from_dict(cls, dados: dict) -> "ItemEntrada":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            quantidade=float(dados.get("quantidade", 0.0) or 0.0),
            custo=float(dados.get("custo", 0.0) or 0.0),
            entrada_id=dados.get("entrada_id"),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Entrada:
    motivo_id: int | None = None
    motivo_codigo: str = ""      # exibição (JOIN com motivos)
    motivo_descricao: str = ""   # exibição (JOIN com motivos)
    data_entrada: str = ""  # ISO AAAA-MM-DD
    sequencia: int | None = None
    total_sql: float = 0.0       # total vindo da pesquisa (soma no SQL)
    id: int | None = None
    itens: list[ItemEntrada] = field(default_factory=list)

    @property
    def total(self) -> float:
        if self.itens:
            return sum(i.total for i in self.itens)
        return self.total_sql

    @classmethod
    def from_dict(cls, dados: dict) -> "Entrada":
        return cls(
            motivo_id=dados.get("motivo_id"),
            motivo_codigo=str(dados.get("motivo_codigo", "")),
            motivo_descricao=str(dados.get("motivo_descricao", "")),
            data_entrada=str(dados.get("data_entrada", "")),
            sequencia=dados.get("sequencia"),
            id=dados.get("id"),
            itens=[ItemEntrada.from_dict(i) for i in dados.get("itens", [])],
        )

    def to_dict(self) -> dict:
        return asdict(self)
