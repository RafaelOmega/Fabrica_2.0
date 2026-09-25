# -*- coding: utf-8 -*-
"""Controller da pesquisa de fichas técnicas."""
from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.ficha_tecnica import FichaTecnica
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_ficha_tecnica import Ui_Pesquisa_Fichas_Tecnicas

try:
    from app.services.ficha_tecnica_service import FichaTecnicaService
except ImportError:
    FichaTecnicaService = None

logger = get_logger("pesquisa_ficha_tecnica")

COLUNAS = ["Ficha", "Produto Acabado", "Sacos/Batida"]
COLUNA_STRETCH = 1
DEBOUNCE_MS = 300


class PesquisaFichaTecnicaController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Fichas_Tecnicas()
        self.ui.setupUi(self)

        self._service = FichaTecnicaService() if FichaTecnicaService else None
        if self._service is None:
            logger.warning("FichaTecnicaService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Fichas_Tecnicas.setModel(self._modelo)

        configurar_tabela(
            self.ui.tb_Fichas_Tecnicas,
            coluna_stretch=COLUNA_STRETCH,
            ordenavel=True,
        )

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Fichas_Tecnicas.doubleClicked.connect(self.accept)

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar fichas na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar fichas:\n{exc}")

    def _agendar_filtro(self):
        self._timer_filtro.start(DEBOUNCE_MS)

    def _pesquisar(self):
        self._timer_filtro.stop()
        try:
            filtro = self.ui.txt_Pesquisa.text().strip()
            registros = self._service.pesquisar(
                filtro) if self._service else []
        except Exception as exc:
            logger.exception("Falha na consulta")
            QMessageBox.critical(self, "Erro", f"Falha na consulta:\n{exc}")
            return

        self._modelo.removeRows(0, self._modelo.rowCount())
        for ficha in registros:
            self._modelo.appendRow([
                QStandardItem(str(ficha.id)),
                QStandardItem(ficha.codigo_produto),
                QStandardItem(f"{ficha.sacos_batida:.4f}"),
            ])
        ajustar_larguras(
            self.ui.tb_Fichas_Tecnicas, coluna_stretch=COLUNA_STRETCH)

    def ficha_selecionada(self) -> FichaTecnica | None:
        indice = self.ui.tb_Fichas_Tecnicas.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()
        item = self._modelo.item(linha, 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_id(int(item.text()))
        except Exception as exc:
            logger.exception("Falha ao carregar ficha selecionada")
            QMessageBox.critical(
                self, "Erro", f"Falha ao carregar a ficha:\n{exc}")
            return None
