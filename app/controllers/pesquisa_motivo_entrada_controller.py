# -*- coding: utf-8 -*-
"""Controller da pesquisa de motivos de entrada.

Responsabilidade: APENAS controle de tela (filtro, tabela, selecao).
A consulta e delegada ao MotivoEntradaService.
"""
from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.motivo_entrada import MotivoEntrada
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_motivo_entrada import Ui_Pesquisa_Motivo_Entrada

try:
    from app.services.motivo_entrada_service import MotivoEntradaService
except ImportError:
    MotivoEntradaService = None

logger = get_logger("pesquisa_motivo_entrada")

COLUNAS = ["Código", "Descrição", "Baixa Ficha Técnica"]

# Índice da coluna que recebe a folga horizontal (Descrição)
COLUNA_STRETCH = 1

# Intervalo (ms) para filtrar enquanto digita
DEBOUNCE_MS = 300


class PesquisaMotivoEntradaController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Motivo_Entrada()
        self.ui.setupUi(self)

        self._service = MotivoEntradaService() if MotivoEntradaService else None
        if self._service is None:
            logger.warning(
                "MotivoEntradaService nao encontrado - consulta desativada")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Motivo.setModel(self._modelo)

        configurar_tabela(
            self.ui.tb_Motivo,
            coluna_stretch=COLUNA_STRETCH,
            ordenavel=True,
        )

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Motivo.doubleClicked.connect(self.accept)

        try:
            self._pesquisar()  # carrega a lista ao abrir
        except Exception as exc:
            logger.exception("Falha ao carregar motivos na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar motivos:\n{exc}")

    # ---------------- acoes ----------------

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

        for motivo in registros:
            linha = [
                motivo.codigo,
                motivo.descricao,
                "Sim" if motivo.baixa_producao else "",
            ]
            self._modelo.appendRow([QStandardItem(v) for v in linha])

        ajustar_larguras(self.ui.tb_Motivo, coluna_stretch=COLUNA_STRETCH)

    # ---------------- selecao ----------------

    def motivo_selecionado(self) -> MotivoEntrada | None:
        indice = self.ui.tb_Motivo.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()

        def col(c):
            item = self._modelo.item(linha, c)
            return item.text() if item else ""

        return MotivoEntrada(
            codigo=col(0),
            descricao=col(1),
            baixa_producao=col(2) == "Sim",
        )
