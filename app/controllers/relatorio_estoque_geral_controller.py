# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Estoque Geral.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via RelatorioEstoqueGeralService.
"""
from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.controllers.relatorio_estoque_geral_preview_controller import (
    RelEstoqueGeralPreviewController,
)
from app.services.relatorio_estoque_geral_service import (
    RelatorioEstoqueGeralService,
)
from app.utils.logger import get_logger
from app.views.ui_relatorio_estoque_geral import Ui_Rel_Estoque_Geral

logger = get_logger("relatorio_estoque_geral")


class RelEstoqueGeralController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Rel_Estoque_Geral()
        self.ui.setupUi(self)
        self._service = RelatorioEstoqueGeralService()
        self._produto_id = None

        # período padrão: 1º de janeiro do ano corrente até hoje
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(QDate(hoje.year(), 1, 1))
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar_Produtos.clicked.connect(self._pesquisar_produto)
        self.ui.bt_Filtrar.clicked.connect(self._filtrar)
        self.ui.txt_Produto.textChanged.connect(self._ao_mudar_produto)

    # ---------------- produto ----------------

    def _ao_mudar_produto(self):
        """Limpar o campo manualmente cancela o filtro de produto."""
        if not self.ui.txt_Produto.text().strip():
            self._produto_id = None

    def _pesquisar_produto(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._produto_id = produto.id
                self.ui.txt_Produto.setText(
                    f"{produto.codigo} - {produto.descricao}")

    # ---------------- filtro ----------------

    def _filtrar(self):
        data_inicial = self.ui.dt_Data_Inicial.date().toString("yyyy-MM-dd")
        data_final = self.ui.dt_Data_Final.date().toString("yyyy-MM-dd")
        if data_final < data_inicial:
            QMessageBox.warning(
                self, "Atenção",
                "A data final deve ser maior ou igual à data inicial.")
            self.ui.dt_Data_Final.setFocus()
            return
        try:
            linhas = self._service.estoque(
                self._produto_id, data_inicial, data_final)
        except Exception as exc:
            logger.exception("Falha ao gerar o relatório de estoque")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível gerar o relatório:\n{exc}")
            return
        di = datetime.strptime(data_inicial, "%Y-%m-%d").strftime("%d/%m/%Y")
        df = datetime.strptime(data_final, "%Y-%m-%d").strftime("%d/%m/%Y")
        dialogo = RelEstoqueGeralPreviewController(
            linhas, f"Período: {di} a {df}", self)
        dialogo.exec()
