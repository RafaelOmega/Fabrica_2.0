# -*- coding: utf-8 -*-
"""Tela de abertura (splash) do sistema.

Mostra o progresso da inicialização (conexão, schema, janela
principal). O main.py chama atualizar() a cada etapa concluída;
o processEvents repinta a tela antes do próximo passo bloqueante.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from app.utils.logger import get_logger
from app.views.ui_carregamento import Ui_Carregamento

logger = get_logger("carregamento")


class CarregamentoController(QDialog):
    """Splash frameless com barra de progresso da inicialização."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Carregamento()
        self.ui.setupUi(self)
        # splash: sem borda, sem botões, sempre visível durante a abertura
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint)
        self.ui.progressBar.setValue(0)

    def atualizar(self, porcentagem: int, texto: str = ""):
        """Avança a barra e, opcionalmente, troca a mensagem da etapa."""
        self.ui.progressBar.setValue(porcentagem)
        if texto:
            self.ui.lb_Carregamento.setText(texto)
        # repinta antes do próximo passo bloqueante (conexão, schema...)
        QApplication.processEvents()
