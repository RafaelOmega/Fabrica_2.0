# -*- coding: utf-8 -*-
"""Modelos de domínio Saída e seus itens."""
from dataclasses import asdict, dataclass, field


@dataclass
class ItemSaida:
    produto_id: int | None = None
    codigo_produto: str = ""
    descricao_produto: str = ""
    quantidade: float = 0.0
    custo: float = 0.0
    saida_id: int | None = None
    id: int | None = None

    @property
    def total(self) -> float:
        return self.quantidade * self.custo

    @classmethod
    def from_dict(cls, dados: dict) -> "ItemSaida":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            descricao_produto=str(dados.get("descricao_produto", "")),
            quantidade=float(dados.get("quantidade", 0.0) or 0.0),
            custo=float(dados.get("custo", 0.0) or 0.0),
            saida_id=dados.get("saida_id"),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ItemSaidaMaoObra:
    """Mão de obra vinculada à saída (não controla estoque; não vai ao kardex)."""
    produto_id: int | None = None
    codigo_produto: str = ""
    descricao_produto: str = ""
    quantidade: float = 0.0
    custo: float = 0.0
    saida_id: int | None = None
    id: int | None = None

    @property
    def total(self) -> float:
        return self.quantidade * self.custo

    @classmethod
    def from_dict(cls, dados: dict) -> "ItemSaidaMaoObra":
        return cls(
            produto_id=dados.get("produto_id"),
            codigo_produto=str(dados.get("codigo_produto", "")),
            descricao_produto=str(dados.get("descricao_produto", "")),
            quantidade=float(dados.get("quantidade", 0.0) or 0.0),
            custo=float(dados.get("custo", 0.0) or 0.0),
            saida_id=dados.get("saida_id"),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Saida:
    data_saida: str = ""
    destino: str = ""
    retirada: str = ""
    sequencia: int | None = None
    total_sql: float = 0.0
    id: int | None = None
    itens: list[ItemSaida] = field(default_factory=list)
    mao_obra: list[ItemSaidaMaoObra] = field(default_factory=list)

    @property
    def total(self) -> float:
        if self.itens:
            return sum(i.total for i in self.itens)
        return self.total_sql

    @classmethod
    def from_dict(cls, dados: dict) -> "Saida":
        return cls(
            data_saida=str(dados.get("data_saida", "")),
            destino=str(dados.get("destino", "")),
            retirada=str(dados.get("retirada", "")),
            sequencia=dados.get("sequencia"),
            total_sql=float(dados.get("total_sql", 0.0) or 0.0),
            id=dados.get("id"),
            itens=[ItemSaida.from_dict(i) for i in dados.get("itens", [])],
            mao_obra=[ItemSaidaMaoObra.from_dict(m)
                      for m in dados.get("mao_obra", [])],
        )

    def to_dict(self) -> dict:
        return asdict(self)
