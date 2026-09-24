# -*- coding: utf-8 -*-
"""Ponto de entrada do sistema Fábrica."""
import sys

from PySide6.QtWidgets import QApplication

from app.controllers.main_window_controller import MainWindowController
from app.utils.logger import get_logger, setup_logging
from app.utils.theme import aplicar_tema

logger = get_logger("main")


def main() -> int:
    setup_logging()
    logger.info("Iniciando Fábrica...")

    app = QApplication(sys.argv)
    app.setApplicationName("Fábrica")
    app.setOrganizationName("Fábrica")

    aplicar_tema(app)

    janela = MainWindowController()
    janela.show()

    logger.info("Aplicação iniciada")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
