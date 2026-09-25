# -*- coding: utf-8 -*-
"""Ícones da aplicação, com caminhos compatíveis com PyInstaller."""
import sys
from pathlib import Path

from PySide6.QtGui import QIcon

from app.utils.logger import get_logger

logger = get_logger("icons")

# Ícone principal do projeto (raiz do repositório)
NOME_ICONE = "Omega-1.ico"


def _base_path() -> Path:
    """
    Retorna a base correta dos arquivos:
    - desenvolvimento: raiz do projeto
    - executável PyInstaller: pasta do bundle (_MEIPASS)
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]


def caminho_icone(nome: str = NOME_ICONE) -> Path | None:
    """Localiza um ícone em caminhos compatíveis com dev e PyInstaller."""
    base = _base_path()

    candidatos = [
        base / nome,                # PyInstaller (--add-data "Omega-1.ico;.")
        base / "assets" / nome,     # se um dia mover para assets/
        base / "app" / "assets" / nome,
    ]

    for caminho in candidatos:
        if caminho.exists():
            return caminho

    return None


def icone_aplicacao() -> QIcon:
    """Retorna o QIcon da aplicação (vazio se não encontrar o arquivo)."""
    caminho = caminho_icone()
    if caminho is None:
        logger.warning("Ícone %s não encontrado", NOME_ICONE)
        return QIcon()

    return QIcon(str(caminho))


def aplicar_icone_aplicacao(app) -> None:
    """Define o ícone da aplicação.

    O ícone da QApplication propaga automaticamente para todas as
    janelas e dialogs que não tenham ícone próprio — incluindo as
    subjanelas do MDI e as telas de pesquisa.
    """
    icone = icone_aplicacao()
    if not icone.isNull():
        app.setWindowIcon(icone)
        logger.info("Ícone da aplicação aplicado: %s", NOME_ICONE)
