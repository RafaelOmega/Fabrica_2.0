# -*- coding: utf-8 -*-
"""Ponto de entrada do sistema Fábrica."""
import ctypes
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.controllers.main_window_controller import MainWindowController
from app.database import get_connection
from app.utils.logger import get_logger, setup_logging
from app.utils.theme import aplicar_tema
from app.utils.icons import aplicar_icone_aplicacao

logger = get_logger("main")


def _validar_conexao() -> bool:
    """Tenta conectar ao banco. Retorna True se conectou."""
    try:
        conn = get_connection()
        conn.close()
        logger.info("Conexão com o banco validada")
        return True
    except Exception as exc:
        logger.error("Falha ao conectar no banco: %s", exc)
        return False


def _definir_app_id() -> None:
    """Define o AppUserModelID para o Windows usar o ícone correto
    na barra de tarefas (em vez do ícone do python.exe)."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Omega.ControleFabrica.2.0"
        )
    except Exception:
        pass  # não é Windows ou falhou -> segue sem o ID


def main() -> int:
    setup_logging()
    logger.info("Iniciando Fábrica...")

    _definir_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName("Fábrica")
    app.setOrganizationName("Fábrica")

    aplicar_tema(app)
    aplicar_icone_aplicacao(app)

    if not _validar_conexao():
        resposta = QMessageBox.question(
            None,
            "Banco de dados",
            "Não foi possível conectar ao banco de dados.\n\n"
            "Deseja continuar mesmo assim?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            logger.info("Aplicação encerrada pelo usuário (sem banco)")
            return 0

    janela = MainWindowController()
    janela.showMaximized()

    logger.info("Aplicação iniciada")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
