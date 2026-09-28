# -*- coding: utf-8 -*-
"""Service do relatório de kardex do produto."""
from datetime import date

from app.models.relatorio_kardex import KardexProduto
from app.repositories.relatorio_kardex_repository import (
    RelatorioKardexRepository,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_kardex_service")


class RelatorioKardexService:

    def __init__(self):
        self._repo = RelatorioKardexRepository()

    def kardex(self, filtro: str, data_inicial: date,
               data_final: date) -> list[KardexProduto]:
        """Dados prontos para o relatório, com saldo acumulado por linha."""
        produtos = self._repo.kardex(filtro, data_inicial, data_final)
        for produto in produtos:
            saldo = produto.saldo_inicial
            for movimento in produto.movimentos:
                saldo += movimento.entrada - movimento.saida
                movimento.saldo = saldo
        return produtos
