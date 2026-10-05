# -*- coding: utf-8 -*-
"""Service do relatório de entradas."""
from datetime import date

from app.models.relatorio_entrada import RelatorioEntrada
from app.repositories.relatorio_entrada_repository import (
    RelatorioEntradaRepository,
)


class RelatorioEntradaService:

    def __init__(self):
        self._repo = RelatorioEntradaRepository()

    def relatorio(self, data_inicial: date, data_final: date,
                  entrada_id: int | None = None) -> RelatorioEntrada:
        return self._repo.relatorio(data_inicial, data_final, entrada_id)
