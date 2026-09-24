# -*- coding: utf-8 -*-
"""Controller do cadastro de produtos.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao ProdutoService.
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.logger import get_logger
from app.views.ui_cad_produtos import Ui_Cad_Produtos

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None  # service ainda não criado

logger = get_logger("cad_produtos")


class CadProdutosController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Produtos()
        self.ui.setupUi(self)

        self._service = ProdutoService() if ProdutoService else None
        if self._service is None:
            logger.warning(
                "ProdutoService nao encontrado - acoes de dados desativadas")

        self._conectar_botoes()
        self._limpar_campos()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Produtos.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._editar)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    # ---------------- acoes de tela ----------------

    def _novo(self):
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _pesquisar(self):
        from app.controllers.pesquisa_produto_controller import PesquisaProdutoController
        try:
            dialogo = PesquisaProdutoController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._preencher(produto)

    def _salvar(self):
        if self._service is None:
            logger.warning("Salvar ignorado: service nao implementado")
            return
        self._service.salvar(self._coletar_dados())
        logger.info("Salvar acionado")

    def _editar(self):
        if self._service is None:
            logger.warning("Editar ignorado: service nao implementado")
            return
        self._service.atualizar(self._coletar_dados())
        logger.info("Editar acionado")

    def _excluir(self):
        if self._service is None:
            logger.warning("Excluir ignorado: service nao implementado")
            return
        self._service.excluir(self.ui.txt_Codigo.text().strip())
        logger.info("Excluir acionado")

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()
        self.ui.txt_Peso.setValue(0.0)
        self.ui.txt_Custo.setValue(0.0)
        self.ui.ch_Mat_Prima.setChecked(False)
        self.ui.ch_Prod_Acabado.setChecked(False)
        self.ui.ch_Mao_Obra.setChecked(False)
        self.ui.ch_Controla_Estoque.setChecked(False)

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "descricao": self.ui.txt_Descricao.text().strip(),
            "peso": self.ui.txt_Peso.value(),
            "custo": self.ui.txt_Custo.value(),
            "mat_prima": self.ui.ch_Mat_Prima.isChecked(),
            "prod_acabado": self.ui.ch_Prod_Acabado.isChecked(),
            "mao_obra": self.ui.ch_Mao_Obra.isChecked(),
            "controla_estoque": self.ui.ch_Controla_Estoque.isChecked(),
        }

    def _preencher(self, produto):
        self._limpar_campos()
        self.ui.txt_Codigo.setText(produto.codigo)
        self.ui.txt_Descricao.setText(produto.descricao)
        self.ui.txt_Peso.setValue(produto.peso)
        self.ui.txt_Custo.setValue(produto.custo)
        self.ui.ch_Mat_Prima.setChecked(produto.mat_prima)
        self.ui.ch_Prod_Acabado.setChecked(produto.prod_acabado)
        self.ui.ch_Mao_Obra.setChecked(produto.mao_obra)
        self.ui.ch_Controla_Estoque.setChecked(produto.controla_estoque)
