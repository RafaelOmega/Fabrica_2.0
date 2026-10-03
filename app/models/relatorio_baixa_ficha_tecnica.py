# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de baixa de ficha técnica."""
from dataclasses import dataclass, field


@dataclass
class ItemBaixaFicha:
    """Insumo baixado de uma ficha técnica (item consumido na produção)."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade: float = 0.0   # quantidade gravada no kardex (sacos ou kg)
    custo: float = 0.0        # custo unitário do insumo no momento da baixa

    @property
    def total(self) -> float:
        return self.quantidade * self.custo


@dataclass
class AcabadoBaixa:
    """Produto acabado da entrada de produção."""
    produto_id: int | None = None
    codigo: str = ""
    descricao: str = ""
    quantidade: float = 0.0
    custo: float = 0.0

    @property
    def total(self) -> float:
        return self.quantidade * self.custo


@dataclass
class BaixaFichaTecnica:
    """Uma baixa de ficha técnica = uma entrada de produção."""
    entrada_id: int | None = None
    sequencia: int | None = None
    data_entrada: str = ""
    motivo_descricao: str = ""
    acabados: list[AcabadoBaixa] = field(default_factory=list)
    itens: list[ItemBaixaFicha] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(i.total for i in self.itens)

    @property
    def acabado_texto(self) -> str:
        return " | ".join(
            f"{a.codigo} - {a.descricao}" for a in self.acabados)


@dataclass
class RelatorioBaixaFichaTecnica:
    """Relatório de baixas: entrada a entrada, com acabados e itens."""
    data_inicial: str = ""
    data_final: str = ""
    linhas: list[BaixaFichaTecnica] = field(default_factory=list)

    @property
    def total_geral(self) -> float:
        return sum(l.total for l in self.linhas)
