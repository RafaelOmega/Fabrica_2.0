# -*- coding: utf-8 -*-
"""Service de motivos de entrada: regras de negócio."""
from app.models.motivo_entrada import MotivoEntrada
from app.repositories.motivo_entrada_repository import MotivoEntradaRepository
from app.utils.logger import get_logger

logger = get_logger("motivo_entrada_service")


class MotivoEntradaService:

    def __init__(self):
        self._repo = MotivoEntradaRepository()

    def salvar(self, dados: dict) -> MotivoEntrada:
        return self._repo.inserir(MotivoEntrada.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(MotivoEntrada.from_dict(dados))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def buscar_por_codigo(self, codigo: str) -> MotivoEntrada | None:
        return self._repo.buscar_por_codigo(codigo)

    def pesquisar(self, filtro: str = "") -> list[MotivoEntrada]:
        return self._repo.pesquisar(filtro)
