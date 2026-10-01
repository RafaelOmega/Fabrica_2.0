# -*- coding: utf-8 -*-
"""Service de unidades de medida: regras de negócio."""
from app.models.unidade_medida import UnidadeMedida
from app.repositories.unidade_medida_repository import UnidadeMedidaRepository
from app.utils.logger import get_logger

logger = get_logger("unidade_medida_service")


class UnidadeMedidaService:

    def __init__(self):
        self._repo = UnidadeMedidaRepository()

    def salvar(self, dados: dict) -> UnidadeMedida:
        return self._repo.salvar(UnidadeMedida.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(UnidadeMedida.from_dict(dados))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def buscar_por_codigo(self, codigo: str) -> UnidadeMedida | None:
        return self._repo.buscar_por_codigo(codigo)

    def pesquisar(self, filtro: str = "") -> list[UnidadeMedida]:
        return self._repo.pesquisar(filtro)
