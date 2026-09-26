# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Fichas Técnicas.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via RelatorioFichaTecnicaService.
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_ficha_tecnica_service import (
    RelatorioFichaTecnicaService,
)
from app.utils.logger import get_logger
from app.views.ui_relatorio_ficha_tecnica import Ui_Rel_Ficha_Tecnica

logger = get_logger("relatorio_ficha_tecnica")


class RelFichaTecnicaController(QWidget):
    """Tela de filtros do relatório de fichas técnicas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Ficha_Tecnica()
        self.ui.setupUi(self)

        self._service = RelatorioFichaTecnicaService()

        self.ui.bt_Pesquisar_Fichas_Tecnicas.clicked.connect(
            self._pesquisar_ficha)
        self.ui.bt_Filtrar.clicked.connect(self._gerar_relatorio)

    # ---------------- filtros ----------------

    def _pesquisar_ficha(self):
        """Abre a pesquisa de fichas e copia a descrição do produto acabado."""
        from app.controllers.pesquisa_ficha_tecnica_controller import (
            PesquisaFichaTecnicaController,
        )
        dialogo = PesquisaFichaTecnicaController(self)
        if dialogo.exec():
            ficha = dialogo.ficha_selecionada()   # método, com parênteses
            if ficha:
                descricao = self._service.descricao_da_ficha(ficha.id)
                self.ui.txt_Fichas_Tecnicas.setText(descricao or
                                                    ficha.codigo_produto)

    # ---------------- geração ----------------

    def _gerar_relatorio(self):
        filtro = self.ui.txt_Fichas_Tecnicas.text().strip()
        try:
            fichas = self._service.fichas_tecnicas(filtro)
        except Exception as exc:
            QMessageBox.critical(self, "Relatório", self._mensagem_erro(exc))
            return

        if not fichas:
            QMessageBox.information(
                self, "Relatório", "Nenhuma ficha técnica encontrada.")
            return

        # pré-visualização: mesmo layout do PDF, com PDF/XLSX/CSV
        # (fichas não têm data — nenhum período é informado)
        from app.controllers.relatorio_ficha_tecnica_preview_controller import (
            RelFichaTecnicaPreviewController,
        )
        dialogo = RelFichaTecnicaPreviewController(fichas, "", self)
        dialogo.exec()

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        nome = type(exc).__name__
        if nome == "OperationalError":
            return "Falha de conexão com o banco de dados."
        return f"Erro ao gerar o relatório: {exc}"
