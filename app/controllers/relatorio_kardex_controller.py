# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Kardex do Produto.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via RelatorioKardexService.
"""
from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_kardex_service import RelatorioKardexService
from app.utils.logger import get_logger
from app.utils.erros import mensagem_erro
from app.views.ui_relatorio_kardex import Ui_Rel_Kardex

logger = get_logger("relatorio_kardex")


class RelKardexController(QWidget):
    """Tela de filtros do relatório de kardex do produto."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Kardex()
        self.ui.setupUi(self)

        self._service = RelatorioKardexService()

        # padrão: mês corrente
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(QDate(hoje.year(), hoje.month(), 1))
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar_Produtos.clicked.connect(self._pesquisar_produto)
        self.ui.bt_Filtrar.clicked.connect(self._gerar_relatorio)

    # ---------------- filtros ----------------

    def _pesquisar_produto(self):
        """Abre a pesquisa de produtos e copia o código para o filtro."""
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec():
            produto = dialogo.produto_selecionado()
            if produto:
                self.ui.txt_Produto.setText(produto.codigo)

    # ---------------- geração ----------------

    def _gerar_relatorio(self):
        data_inicial = date.fromisoformat(
            self.ui.dt_Data_Inicial.date().toString("yyyy-MM-dd"))
        data_final = date.fromisoformat(
            self.ui.dt_Data_Final.date().toString("yyyy-MM-dd"))
        if data_inicial > data_final:
            QMessageBox.warning(
                self, "Atenção", "Data inicial maior que a data final.")
            return

        filtro = self.ui.txt_Produto.text().strip()
        try:
            kardex_list = self._service.kardex(
                filtro, data_inicial, data_final)
        except Exception as exc:
            QMessageBox.critical(self, "Relatório", self._mensagem_erro(exc))
            return

        if not kardex_list:
            QMessageBox.information(
                self, "Relatório",
                "Nenhum produto com movimentação no período.")
            return

        periodo = (
            f"Período: {self.ui.dt_Data_Inicial.date().toString('dd/MM/yyyy')}"
            f" a {self.ui.dt_Data_Final.date().toString('dd/MM/yyyy')}"
        )

        # pré-visualização: mesmo layout do PDF, com PDF/XLSX/CSV
        from app.controllers.relatorio_kardex_preview_controller import (
            RelKardexPreviewController,
        )
        dialogo = RelKardexPreviewController(kardex_list, periodo, self)
        dialogo.exec()

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(exc, prefixo="Erro ao gerar o relatório")
