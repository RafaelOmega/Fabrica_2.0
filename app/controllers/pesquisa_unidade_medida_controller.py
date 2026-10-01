# -*- coding: utf-8 -*-
"""Controller da pesquisa de unidades de medida."""
from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.unidade_medida import UnidadeMedida
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_unidade_medida import Ui_Pesquisa_Unidade_Medida

try:
    from app.services.unidade_medida_service import UnidadeMedidaService
except ImportError:
    UnidadeMedidaService = None

logger = get_logger("pesquisa_unidade_medida")
COLUNAS = ["Código", "Descrição", "Fator"]
COLUNA_STRETCH = 1
DEBOUNCE_MS = 300


class PesquisaUnidadeMedidaController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Unidade_Medida()
        self.ui.setupUi(self)

        self._service = (UnidadeMedidaService()
                         if UnidadeMedidaService else None)
        if self._service is None:
            logger.warning("UnidadeMedidaService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Unidade.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Unidade, coluna_stretch=COLUNA_STRETCH,
                          ordenavel=True)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Unidade.doubleClicked.connect(self.accept)

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar unidades na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar unidades:\n{exc}")

    def _agendar_filtro(self):
        self._timer_filtro.start(DEBOUNCE_MS)

    def _pesquisar(self):
        self._timer_filtro.stop()
        try:
            filtro = self.ui.txt_Pesquisa.text().strip()
            registros = (self._service.pesquisar(filtro)
                         if self._service else [])
        except Exception as exc:
            logger.exception("Falha na consulta")
            QMessageBox.critical(self, "Erro", f"Falha na consulta:\n{exc}")
            return

        self._modelo.removeRows(0, self._modelo.rowCount())
        for unidade in registros:
            fator = f"{unidade.fator_conversao:.4f}".replace(".", ",")
            self._modelo.appendRow([
                QStandardItem(unidade.codigo),
                QStandardItem(unidade.descricao),
                QStandardItem(fator),
            ])
        ajustar_larguras(self.ui.tb_Unidade, coluna_stretch=COLUNA_STRETCH)

    def unidade_selecionada(self) -> UnidadeMedida | None:
        indice = self.ui.tb_Unidade.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()
        item = self._modelo.item(linha, 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar unidade selecionada")
            QMessageBox.critical(
                self, "Erro", f"Falha ao carregar a unidade:\n{exc}")
            return None
