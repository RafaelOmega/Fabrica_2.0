# -*- coding: utf-8 -*-
"""Controller da pesquisa de entradas."""
from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.entrada import Entrada
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_entrada import Ui_Pesquisa_Entrada

try:
    from app.services.entrada_service import EntradaService
except ImportError:
    EntradaService = None

logger = get_logger("pesquisa_entrada")
COLUNAS = ["Sequência", "Data", "Motivo", "Total (R$)"]
COLUNA_STRETCH = 2
DEBOUNCE_MS = 300


def _moeda(valor: float) -> str:
    """Formata valor no padrão monetário brasileiro: R$ 1.234,56."""
    texto = f"{valor:,.2f}"  # 1,234.56 (padrão US)
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class PesquisaEntradaController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Entrada()
        self.ui.setupUi(self)

        self._service = EntradaService() if EntradaService else None
        if self._service is None:
            logger.warning("EntradaService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Entradas.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Entradas, coluna_stretch=COLUNA_STRETCH,
                          ordenavel=True)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Entradas.doubleClicked.connect(self.accept)

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar entradas na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar entradas:\n{exc}")

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
        for entrada in registros:
            data = entrada.data_entrada
            if len(data) == 10:
                ano, mes, dia = data.split("-")
                data = f"{dia}/{mes}/{ano}"
            self._modelo.appendRow([
                QStandardItem(str(entrada.id)),
                QStandardItem(data),
                QStandardItem(
                    entrada.motivo_descricao or entrada.motivo_codigo),
                QStandardItem(_moeda(entrada.total)),
            ])
        ajustar_larguras(self.ui.tb_Entradas, coluna_stretch=COLUNA_STRETCH)

    def entrada_selecionada(self) -> Entrada | None:
        indice = self.ui.tb_Entradas.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()
        item = self._modelo.item(linha, 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_id(int(item.text()))
        except Exception as exc:
            logger.exception("Falha ao carregar entrada selecionada")
            QMessageBox.critical(
                self, "Erro", f"Falha ao carregar a entrada:\n{exc}")
            return None
