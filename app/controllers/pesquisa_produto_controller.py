# -*- coding: utf-8 -*-
"""Controller da pesquisa de produtos.

Responsabilidade: APENAS controle de tela (filtro, tabela, selecao).
A consulta e delegada ao ProdutoService.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.produto import Produto
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_produto import Ui_Pesquisa_Prod

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None  # service ainda não criado

logger = get_logger("pesquisa_produto")

COLUNAS = ["Código", "Descrição", "Matéria Prima", "Prod. Acabado",
           "Mão de Obra", "Peso (Kg)", "Custo (R$)", "Ctrl. Estoque"]

# Índice da coluna que recebe a folga horizontal (Descrição)
COLUNA_STRETCH = 1

# Intervalo (ms) para filtrar enquanto digita
DEBOUNCE_MS = 300


class PesquisaProdutoController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Prod()
        self.ui.setupUi(self)

        self._service = ProdutoService() if ProdutoService else None
        if self._service is None:
            logger.warning(
                "ProdutoService nao encontrado - consulta desativada")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Produtos.setModel(self._modelo)

        # Tabela responsiva: ajusta colunas ao conteúdo e à largura
        configurar_tabela(
            self.ui.tb_Produtos,
            coluna_stretch=COLUNA_STRETCH,
            ordenavel=True,
        )

        # Filtro ao digitar (com debounce para não consultar a cada tecla)
        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Produtos.doubleClicked.connect(self.accept)

        try:
            self._pesquisar()  # carrega a lista ao abrir
        except Exception as exc:
            logger.exception("Falha ao carregar produtos na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar produtos:\n{exc}")

    # ---------------- acoes ----------------

    def _agendar_filtro(self):
        """Agenda a consulta após pausa na digitação."""
        self._timer_filtro.start(DEBOUNCE_MS)

    def _pesquisar(self):
        self._timer_filtro.stop()  # cancela agendamento pendente
        try:
            filtro = self.ui.txt_Pesquisa.text().strip()
            registros = self._service.pesquisar(
                filtro) if self._service else []
        except Exception as exc:
            logger.exception("Falha na consulta")
            QMessageBox.critical(self, "Erro", f"Falha na consulta:\n{exc}")
            return

        self._modelo.removeRows(0, self._modelo.rowCount())

        for produto in registros:
            linha = [
                produto.codigo,
                produto.descricao,
                "Sim" if produto.mat_prima else "",
                "Sim" if produto.prod_acabado else "",
                "Sim" if produto.mao_obra else "",
                str(produto.peso),
                str(produto.custo),
                "Sim" if produto.controla_estoque else "",
            ]
            self._modelo.appendRow([QStandardItem(v) for v in linha])

        # Recalcula larguras após os dados mudarem
        ajustar_larguras(self.ui.tb_Produtos, coluna_stretch=COLUNA_STRETCH)

    # ---------------- selecao ----------------

    def produto_selecionado(self) -> Produto | None:
        indice = self.ui.tb_Produtos.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()

        item = self._modelo.item(linha, 0)
        if item is None or self._service is None:
            return None

        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar produto selecionado")
            QMessageBox.critical(
                self, "Erro", f"Falha ao carregar o produto:\n{exc}")
            return None
