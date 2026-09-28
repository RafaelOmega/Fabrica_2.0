# -*- coding: utf-8 -*-
"""Service de saídas: regras de negócio."""
from app.models.saida import Saida
from app.repositories.saida_repository import SaidaRepository
from app.utils.logger import get_logger

logger = get_logger("saida_service")


class SaidaService:

    def __init__(self):
        self._repo = SaidaRepository()

    def salvar(self, saida: Saida) -> Saida:
        return self._repo.salvar(saida)

    def atualizar(self, saida: Saida) -> bool:
        return self._repo.atualizar(saida)

    def excluir(self, saida_id: int) -> bool:
        return self._repo.excluir(saida_id)

    def buscar_por_id(self, saida_id: int) -> Saida | None:
        return self._repo.buscar_por_id(saida_id)

    def buscar_por_sequencia(self, sequencia: int) -> Saida | None:
        return self._repo.buscar_por_sequencia(sequencia)

    def pesquisar(self, filtro: str = "") -> list[Saida]:
        return self._repo.pesquisar(filtro)

    def saldo_atual(self, produto_id: int) -> float:
        return self._repo.saldo_atual(produto_id)
