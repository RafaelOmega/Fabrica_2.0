# -*- coding: utf-8 -*-
"""Service do relatório de baixa de ficha técnica."""
from datetime import date

from app.models.relatorio_baixa_ficha_tecnica import (
    RelatorioBaixaFichaTecnica,
)
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.repositories.relatorio_baixa_ficha_tecnica_repository import (
    RelatorioBaixaFichaTecnicaRepository,
)


class RelatorioBaixaFichaTecnicaService:

    def __init__(self):
        self._repo = RelatorioBaixaFichaTecnicaRepository()
        self._ficha_repo = FichaTecnicaRepository()

    def relatorio(self, data_inicial: date, data_final: date,
                  ficha_produto_id: int | None = None
                  ) -> RelatorioBaixaFichaTecnica:
        return self._repo.relatorio(data_inicial, data_final,
                                    ficha_produto_id)

    def descricao_da_ficha(self, ficha_id: int) -> str:
        """Descrição do produto acabado da ficha (para o campo de filtro)."""
        ficha = self._ficha_repo.buscar_por_id(ficha_id)
        if ficha is None:
            return ""
        return ficha.descricao_produto or ficha.codigo_produto
