# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de entradas."""
from dataclasses import dataclass, field


@dataclass
class ItemRelatorioEntrada:
    """Produto lançado em uma entrada (insumo ou acabado)."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade: float = 0.0
    custo: float = 0.0

    @property
    def total(self) -> float:
        return self.quantidade * self.custo


@dataclass
class LinhaEntrada:
    """Uma entrada do relatório: cabeçalho + itens lançados."""
    entrada_id: int | None = None
    sequencia: int | None = None
    data_entrada: str = ""
    motivo_descricao: str = ""
    itens: list[ItemRelatorioEntrada] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(i.total for i in self.itens)


@dataclass
class RelatorioEntrada:
    """Relatório de entradas do período.

    Filtros: entrada específica e/ou produto (com modo só_produto).
    """
    data_inicial: str = ""
    data_final: str = ""
    entrada_id: int | None = None
    produto_id: int | None = None
    so_produto: bool = False
    linhas: list[LinhaEntrada] = field(default_factory=list)

    @property
    def tem_dados(self) -> bool:
        return bool(self.linhas)

    @property
    def total_geral(self) -> float:
        return sum(l.total for l in self.linhas)
