# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de baixa de ficha técnica."""
from dataclasses import dataclass, field


@dataclass
class ItemComposicao:
    """Insumo consumido para produzir um lote de produto acabado."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade_sacos: float = 0.0   # convertido pelo fator da unidade
    custo: float = 0.0              # custo unitário do insumo
    origem_entrada_id: int | None = None
    origem_sequencia: int | None = None
    origem_data: str = ""

    @property
    def total(self) -> float:
        return self.quantidade_sacos * self.custo


@dataclass
class ProducaoAcabado:
    """Produção de um acabado dentro de uma entrada (origem da baixa)."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade: float = 0.0        # sacos produzidos do acabado
    custo_acabado: float = 0.0
    entrada_id: int | None = None
    sequencia: int | None = None
    data_entrada: str = ""
    itens: list[ItemComposicao] = field(default_factory=list)

    @property
    def total_acabado(self) -> float:
        return self.quantidade * self.custo_acabado

    @property
    def total_insumos(self) -> float:
        return sum(i.total for i in self.itens)


@dataclass
class GrupoAcabado:
    """Produto acabado e todas as suas produções no período."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    producoes: list[ProducaoAcabado] = field(default_factory=list)

    @property
    def total_quantidade(self) -> float:
        return sum(p.quantidade for p in self.producoes)

    @property
    def total_insumos(self) -> float:
        return sum(p.total_insumos for p in self.producoes)


@dataclass
class RelatorioBaixaFichaTecnica:
    """Relatório: por produto acabado, o que compôs cada produção."""
    data_inicial: str = ""
    data_final: str = ""
    grupos: list[GrupoAcabado] = field(default_factory=list)

    @property
    def total_geral(self) -> float:
        return sum(g.total_insumos for g in self.grupos)
