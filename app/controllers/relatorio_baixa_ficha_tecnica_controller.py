# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Baixa de Ficha Técnica.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via service.
"""
from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_baixa_ficha_tecnica_service import (
    RelatorioBaixaFichaTecnicaService,
)
from app.utils.logger import get_logger
from app.views.ui_relatorio_baixa_ficha_tecnica import (
    Ui_Rel_Baixa_Ficha_Tecnica,
)

logger = get_logger("relatorio_baixa_ficha_tecnica")


class RelBaixaFichaTecnicaController(QWidget):
    """Tela de filtros do relatório de baixa de ficha técnica."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Baixa_Ficha_Tecnica()
        self.ui.setupUi(self)

        self._service = RelatorioBaixaFichaTecnicaService()
        self._ficha_produto_id = None

        # padrão: mês corrente
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(QDate(hoje.year(), hoje.month(), 1))
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar_Ficha_Tecnica.clicked.connect(
            self._pesquisar_ficha)
        self.ui.bt_Filtrar.clicked.connect(self._filtrar)
        self.ui.txt_Ficha_Tecnica.textChanged.connect(self._ao_mudar_ficha)

    # ---------------- ficha tecnica ----------------

    def _ao_mudar_ficha(self):
        """Limpar o campo manualmente cancela o filtro de ficha."""
        if not self.ui.txt_Ficha_Tecnica.text().strip():
            self._ficha_produto_id = None

    def _pesquisar_ficha(self):
        from app.controllers.pesquisa_ficha_tecnica_controller import (
            PesquisaFichaTecnicaController,
        )
        dialogo = PesquisaFichaTecnicaController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            ficha = dialogo.ficha_selecionada()
            if ficha:
                self._ficha_produto_id = ficha.produto_id
                descricao = self._service.descricao_da_ficha(ficha.id)
                self.ui.txt_Ficha_Tecnica.setText(
                    descricao or ficha.codigo_produto)

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
                self._ficha_produto_id,
            )
        except Exception as exc:
            logger.exception("Falha ao gerar o relatório de baixa de ficha")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível gerar o relatório:\n{exc}")
            return

        if not relatorio.linhas:
            QMessageBox.information(
                self, "Relatório",
                "Nenhuma baixa de ficha técnica no período.")
            return

        periodo = (
            f"Período: {self.ui.dt_Data_Inicial.date().toString('dd/MM/yyyy')}"
            f" a {self.ui.dt_Data_Final.date().toString('dd/MM/yyyy')}"
        )

        from app.controllers.relatorio_baixa_ficha_tecnica_preview_controller import (  # noqa: E501
            RelBaixaFichaTecnicaPreviewController,
        )
        dialogo = RelBaixaFichaTecnicaPreviewController(
            relatorio, periodo, self)
        dialogo.exec()
