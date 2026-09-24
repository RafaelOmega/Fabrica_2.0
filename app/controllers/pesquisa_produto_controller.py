# -*- coding: utf-8 -*-
"""Controller da pesquisa de produtos.

Responsabilidade: APENAS controle de tela (filtro, tabela, selecao).
A consulta e delegada ao ProdutoService.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog

from app.utils.logger import get_logger
from app.views.ui_pesquisa_produto import Ui_Pesquisa_Prod

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None  # service ainda não criado

logger = get_logger("pesquisa_produto")

COLUNAS = ["Código", "Descrição", "Matéria Prima", "Prod. Acabado",
           "Mão de Obra", "Peso (Kg)", "Custo (R$)", "Ctrl. Estoque"]


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

        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Produtos.doubleClicked.connect(self.accept)

        self._pesquisar()  # carrega a lista ao abrir

    # ---------------- acoes ----------------

    def _pesquisar(self):
        filtro = self.ui.txt_Pesquisa.text().strip()

        registros = self._service.pesquisar(filtro) if self._service else []
        self._modelo.removeRows(0, self._modelo.rowCount())

        for reg in registros:
            linha = [
                str(reg.get("codigo", "")),
                str(reg.get("descricao", "")),
                "Sim" if reg.get("materia_prima") else "",
                "Sim" if reg.get("produto_acabado") else "",
                "Sim" if reg.get("mao_obra") else "",
                str(reg.get("peso", "")),
                str(reg.get("custo", "")),
                "Sim" if reg.get("controla_estoque") else "",
            ]
            itens = [QStandardItem(valor) for valor in linha]
            self._modelo.appendRow(itens)

        self.ui.tb_Produtos.resizeColumnsToContents()

    # ---------------- selecao ----------------

    def produto_selecionado(self) -> dict | None:
        indice = self.ui.tb_Produtos.currentIndex()
        if not indice.isValid():
            return None

        linha = indice.row()

        def col(c): return self._modelo.item(
            linha, c).text() if self._modelo.item(linha, c) else ""

        return {
            "codigo": col(0),
            "descricao": col(1),
            "materia_prima": col(2) == "Sim",
            "produto_acabado": col(3) == "Sim",
            "mao_obra": col(4) == "Sim",
            "peso": col(5),
            "custo": col(6),
            "controla_estoque": col(7) == "Sim",
        }
