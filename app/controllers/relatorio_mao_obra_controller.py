# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Mão de Obra.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via RelatorioMaoObraService.
"""
from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_mao_obra_service import RelatorioMaoObraService
from app.utils.logger import get_logger
from app.views.ui_relatorio_mao_obra import Ui_Rel_Mao_Obra

logger = get_logger("relatorio_mao_obra")


class RelMaoObraController(QWidget):
    """Tela de filtros do relatório de mão de obra."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Mao_Obra()
        self.ui.setupUi(self)

        self._service = RelatorioMaoObraService()
        self._produto_id = None
        self._produto_codigo = None

        # padrão: mês corrente
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(QDate(hoje.year(), hoje.month(), 1))
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar_Mao_Obra.clicked.connect(self._pesquisar_produto)
        self.ui.bt_Filtrar.clicked.connect(self._filtrar)
        self.ui.txt_Mao_Obra.textChanged.connect(self._ao_mudar_produto)

    # ---------------- produto ----------------

    def _ao_mudar_produto(self):
        """Limpar o campo manualmente cancela o filtro de produto."""
        if not self.ui.txt_Mao_Obra.text().strip():
            self._produto_id = None
            self._produto_codigo = None

    def _pesquisar_produto(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._produto_id = produto.id
                self._produto_codigo = produto.codigo
                self.ui.txt_Mao_Obra.setText(
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
            relatorio = self._service.relatorio(
                date.fromisoformat(data_inicial),
                date.fromisoformat(data_final),
                self._produto_id,
            )
        except Exception as exc:
            logger.exception("Falha ao gerar o relatório de mão de obra")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível gerar o relatório:\n{exc}")
            return

        if not relatorio.linhas:
            QMessageBox.information(
                self, "Relatório",
                "Nenhuma mão de obra no período.")
            return

        periodo = (
            f"Período: {self.ui.dt_Data_Inicial.date().toString('dd/MM/yyyy')}"
            f" a {self.ui.dt_Data_Final.date().toString('dd/MM/yyyy')}"
        )

        from app.controllers.relatorio_mao_obra_preview_controller import (
            RelMaoObraPreviewController,
        )
        dialogo = RelMaoObraPreviewController(relatorio, periodo, self)
        dialogo.exec()
