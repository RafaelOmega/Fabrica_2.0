# -*- coding: utf-8 -*-
"""Service do relatório de mão de obra."""
from datetime import date

from app.models.relatorio_mao_obra import RelatorioMaoObra
from app.repositories.relatorio_mao_obra_repository import (
    RelatorioMaoObraRepository,
)


class RelatorioMaoObraService:

    def __init__(self):
        self._repo = RelatorioMaoObraRepository()

    def relatorio(self, data_inicial: date, data_final: date,
                  produto_id: int | None = None) -> RelatorioMaoObra:
        return self._repo.relatorio(data_inicial, data_final, produto_id)
