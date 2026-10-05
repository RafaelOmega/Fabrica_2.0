# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Entradas.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via service.
"""
from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_entrada_service import RelatorioEntradaService
from app.utils.logger import get_logger
from app.views.ui_relatorio_entrada import Ui_Rel_Entrada

logger = get_logger("relatorio_entrada")


class RelEntradaController(QWidget):
    """Tela de filtros do relatório de entradas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Entrada()
        self.ui.setupUi(self)

        self._service = RelatorioEntradaService()
        self._entrada_id = None

        # padrão: mês corrente
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(QDate(hoje.year(), hoje.month(), 1))
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar_Entrada.clicked.connect(self._pesquisar_entrada)
        self.ui.bt_Filtrar.clicked.connect(self._filtrar)
        self.ui.txt_Entrada.textChanged.connect(self._ao_mudar_entrada)

    # ---------------- entrada ----------------

    def _ao_mudar_entrada(self):
        """Limpar o campo manualmente cancela o filtro de entrada."""
        if not self.ui.txt_Entrada.text().strip():
            self._entrada_id = None

    def _pesquisar_entrada(self):
        from app.controllers.pesquisa_entrada_controller import (
            PesquisaEntradaController,
        )
        dialogo = PesquisaEntradaController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            entrada = dialogo.entrada_selecionada()
            if entrada:
                self._entrada_id = entrada.id
                # padrão dos outros relatórios: código - descrição
                self.ui.txt_Entrada.setText(
                    f"{entrada.sequencia} - {entrada.motivo_descricao}")

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
                self._entrada_id,
            )
        except Exception as exc:
            logger.exception("Falha ao gerar o relatório de entradas")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível gerar o relatório:\n{exc}")
            return

        if not relatorio.tem_dados:
            QMessageBox.information(
                self, "Relatório", "Nenhuma entrada no período.")
            return

        periodo = (
            f"Período: {self.ui.dt_Data_Inicial.date().toString('dd/MM/yyyy')}"
            f" a {self.ui.dt_Data_Final.date().toString('dd/MM/yyyy')}"
        )

        from app.controllers.relatorio_entrada_preview_controller import (
            RelEntradaPreviewController,
        )
        dialogo = RelEntradaPreviewController(relatorio, periodo, self)
        dialogo.exec()
