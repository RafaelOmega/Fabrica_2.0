# -*- coding: utf-8 -*-
"""Service de fichas técnicas: regras de negócio."""
from app.models.ficha_tecnica import FichaTecnica
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.utils.logger import get_logger

logger = get_logger("ficha_tecnica_service")


class FichaTecnicaService:

    def __init__(self):
        self._repo = FichaTecnicaRepository()

    def salvar(self, ficha: FichaTecnica) -> FichaTecnica:
        return self._repo.inserir(ficha)

    def atualizar(self, ficha: FichaTecnica) -> bool:
        return self._repo.atualizar(ficha)

    def excluir(self, ficha_id: int) -> bool:
        return self._repo.excluir(ficha_id)

    def buscar_por_id(self, ficha_id: int) -> FichaTecnica | None:
        return self._repo.buscar_por_id(ficha_id)

    def pesquisar(self, filtro: str = "") -> list[FichaTecnica]:
        return self._repo.pesquisar(filtro)
