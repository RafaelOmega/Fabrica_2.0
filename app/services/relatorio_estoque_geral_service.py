# -*- coding: utf-8 -*-
"""Service do relatório de estoque geral."""
from app.models.relatorio_estoque_geral import LinhaEstoqueGeral
from app.repositories.relatorio_estoque_geral_repository import (
    RelatorioEstoqueGeralRepository,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_estoque_geral_service")


class RelatorioEstoqueGeralService:

    def __init__(self):
        self._repo = RelatorioEstoqueGeralRepository()

    def estoque(self, produto_id: int | None, data_inicial: str,
                data_final: str) -> list[LinhaEstoqueGeral]:
        return self._repo.estoque(produto_id, data_inicial, data_final)
