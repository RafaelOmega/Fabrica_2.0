# -*- coding: utf-8 -*-
"""Service de entradas: regras de negócio."""
from app.models.entrada import Entrada
from app.repositories.entrada_repository import EntradaRepository
from app.utils.logger import get_logger

logger = get_logger("entrada_service")


class EntradaService:

    def __init__(self):
        self._repo = EntradaRepository()

    def salvar(self, entrada: Entrada) -> Entrada:
        return self._repo.salvar(entrada)

    def atualizar(self, entrada: Entrada) -> bool:
        return self._repo.atualizar(entrada)

    def excluir(self, entrada_id: int) -> bool:
        return self._repo.excluir(entrada_id)

    def buscar_por_id(self, entrada_id: int) -> Entrada | None:
        return self._repo.buscar_por_id(entrada_id)

    def pesquisar(self, filtro: str = "") -> list[Entrada]:
        return self._repo.pesquisar(filtro)

    def buscar_por_sequencia(self, sequencia: int) -> Entrada | None:
        return self._repo.buscar_por_sequencia(sequencia)
