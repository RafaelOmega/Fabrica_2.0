# -*- coding: utf-8 -*-
"""Service do relatório de fichas técnicas."""
from app.models.relatorio_ficha_tecnica import FichaTecnicaRelatorio
from app.repositories.relatorio_ficha_tecnica_repository import (
    RelatorioFichaTecnicaRepository,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_ficha_tecnica_service")


class RelatorioFichaTecnicaService:

    def __init__(self):
        self._repo = RelatorioFichaTecnicaRepository()

    def fichas_tecnicas(self, filtro: str = "") -> list[FichaTecnicaRelatorio]:
        """Dados prontos para o PDF. Filtro vazio = todas as fichas."""
        return self._repo.fichas_tecnicas(filtro.strip())

    def descricao_da_ficha(self, ficha_id: int) -> str:
        """Descrição do produto acabado de uma ficha específica."""
        return self._repo.descricao_da_ficha(ficha_id)
