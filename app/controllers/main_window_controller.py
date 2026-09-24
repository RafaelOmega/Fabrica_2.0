# -*- coding: utf-8 -*-
from datetime import datetime

from PySide6.QtCore import QDate, QTime, Qt, QTimer
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from app.utils.logger import get_logger
from app.views.ui_main_window import Ui_MainWindow

logger = get_logger("main_window")


class MainWindowController(QMainWindow):
    """Janela principal (MDI) do sistema Fábrica.

    - Monta a UI gerada pelo Qt Designer
    - Liga as ações dos menus às subjanelas do QMdiArea
    - Mantém data/hora atualizados na barra de status
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._criadores = {}        # chave -> factory do controller da tela
        self._subjanelas = {}       # chave -> QMdiSubWindow aberta

        self._configurar_status_bar()
        self._conectar_acoes()
        self._iniciar_relogio()

        logger.info("Janela principal iniciada")

    # ---------------- configuração ----------------

    def _configurar_status_bar(self):
        self.ui.lb_Comandos.setText("")
        agora = datetime.now()
        self.ui.dt_Data_Atual.setDate(
            QDate(agora.year, agora.month, agora.day))
        self.ui.dt_Hora_Atual.setTime(
            QTime(agora.hour, agora.minute, agora.second))
        self.ui.mdiArea.subWindowActivated.connect(self._ao_ativar_subjanela)

    def _conectar_acoes(self):
        # chave -> (ação do menu, título da janela)
        self._telas = {
            "produtos":       (self.ui.actionProdutos, "Produtos"),
            "motivo_entrada": (self.ui.actionMotivo_Entrada, "Motivo de Entrada"),
            "ficha_tecnica":  (self.ui.actionFicha_Tecnica, "Ficha Técnica"),
            "entrada":        (self.ui.actionEntrada, "Entrada"),
            "saida":          (self.ui.actionSaida, "Saída"),
            "estoque":        (self.ui.actionEstoque, "Estoque"),
            "ficha_kardex":   (self.ui.actionFichaKardexProduto, "Ficha Kardex do Produto"),
        }
        for chave, (acao, _titulo) in self._telas.items():
            acao.triggered.connect(
                lambda _checked=False, c=chave: self._abrir_tela(c)
            )

    def _iniciar_relogio(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._atualizar_relogio)
        self._timer.start(1000)

    # ---------------- abertura de telas ----------------

    def _abrir_tela(self, chave: str):
        titulo = self._telas[chave][1]

        sub = self._subjanelas.get(chave)
        if sub is not None:  # já aberta -> traz para frente
            sub.show()
            sub.raise_()
            self.ui.mdiArea.setActiveSubWindow(sub)
            return

        widget = self._criar_widget(chave, titulo)
        sub = self.ui.mdiArea.addSubWindow(widget)
        sub.setWindowTitle(titulo)
        sub.destroyed.connect(
            lambda _o=None, c=chave: self._subjanelas.pop(c, None))

        self._subjanelas[chave] = sub
        sub.show()
        logger.info("Tela aberta: %s", titulo)

    def _criar_widget(self, chave: str, titulo: str) -> QWidget:
        criador = self._criadores.get(chave)
        if criador is not None:
            return criador(self)

        # Placeholder até a tela ter seu próprio controller.
        # Exemplo de registro quando existir o controller real:
        #   self._criadores["produtos"] = lambda pai: ProdutosController(pai)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        rotulo = QLabel(
            f"{titulo}\n(controller ainda não implementado)", widget
        )
        rotulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rotulo)
        return widget

    # ---------------- status bar ----------------

    def _ao_ativar_subjanela(self, sub):
        self.ui.lb_Comandos.setText(sub.windowTitle() if sub else "")

    def _atualizar_relogio(self):
        agora = datetime.now()
        self.ui.dt_Data_Atual.setDate(
            QDate(agora.year, agora.month, agora.day))
        self.ui.dt_Hora_Atual.setTime(
            QTime(agora.hour, agora.minute, agora.second))
