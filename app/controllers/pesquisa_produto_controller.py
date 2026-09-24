# -*- coding: utf-8 -*-
"""Controller da pesquisa de produtos.

Responsabilidade: APENAS controle de tela (filtro, tabela, selecao).
A consulta e delegada ao ProdutoService.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.produto import Produto
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

        try:
            self._pesquisar()  # carrega a lista ao abrir
        except Exception as exc:
            logger.exception("Falha ao carregar produtos na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar produtos:\n{exc}")

    # ---------------- acoes ----------------

    def _pesquisar(self):
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
                "Sim" if produto.materia_prima else "",
                "Sim" if produto.produto_acabado else "",
                "Sim" if produto.mao_obra else "",
                str(produto.peso),
                str(produto.custo),
                "Sim" if produto.controla_estoque else "",
            ]
            self._modelo.appendRow([QStandardItem(v) for v in linha])

        self.ui.tb_Produtos.resizeColumnsToContents()

    # ---------------- selecao ----------------

    def produto_selecionado(self) -> Produto | None:
        indice = self.ui.tb_Produtos.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()

        def col(c):
            item = self._modelo.item(linha, c)
            return item.text() if item else ""

        return Produto(
            codigo=col(0),
            descricao=col(1),
            materia_prima=col(2) == "Sim",
            produto_acabado=col(3) == "Sim",
            mao_obra=col(4) == "Sim",
            peso=float(col(5) or 0),
            custo=float(col(6) or 0),
            controla_estoque=col(7) == "Sim",
        )
