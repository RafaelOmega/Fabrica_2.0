# -*- coding: utf-8 -*-
"""Controller do cadastro de produtos.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao ProdutoService.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.logger import get_logger
from app.views.ui_cad_produtos import Ui_Cad_Produtos

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None  # service ainda não criado

logger = get_logger("cad_produtos")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"


class CadProdutosController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Produtos()
        self.ui.setupUi(self)

        self._service = ProdutoService() if ProdutoService else None
        if self._service is None:
            logger.warning(
                "ProdutoService nao encontrado - acoes de dados desativadas")

        self._modo = ESTADO_INICIAL
        self._codigo_original = None

        self._conectar_botoes()
        self._conectar_teclas()
        self._limpar_campos()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Produtos.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # Enter no código: busca direta ou abre a pesquisa
        self.ui.txt_Codigo.returnPressed.connect(self._ao_enter_codigo)
        # F2 inicia novo registro (apenas no estado inicial)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        """Abertura: apenas código, pesquisar e novo acessíveis."""
        self.ui.txt_Codigo.setEnabled(True)
        self.ui.bt_Pesquisar_Produtos.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.txt_Descricao.setEnabled(False)
        self.ui.txt_Peso.setEnabled(False)
        self.ui.txt_Custo.setEnabled(False)
        self.ui.ch_Mat_Prima.setEnabled(False)
        self.ui.ch_Prod_Acabado.setEnabled(False)
        self.ui.ch_Mao_Obra.setEnabled(False)
        self.ui.ch_Controla_Estoque.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        """Novo registro: formulário liberado; Editar/Excluir bloqueados."""
        self.ui.txt_Codigo.setEnabled(True)
        self.ui.txt_Descricao.setEnabled(True)
        self.ui.txt_Peso.setEnabled(True)
        self.ui.txt_Custo.setEnabled(True)
        self.ui.ch_Mat_Prima.setEnabled(True)
        self.ui.ch_Prod_Acabado.setEnabled(True)
        self.ui.ch_Mao_Obra.setEnabled(True)
        self.ui.ch_Controla_Estoque.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Produtos.setEnabled(False)

    def _estado_visualizacao(self):
        """Produto carregado: Editar, Limpar e Excluir ativos."""
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Descricao.setEnabled(False)
        self.ui.txt_Peso.setEnabled(False)
        self.ui.txt_Custo.setEnabled(False)
        self.ui.ch_Mat_Prima.setEnabled(False)
        self.ui.ch_Prod_Acabado.setEnabled(False)
        self.ui.ch_Mao_Obra.setEnabled(False)
        self.ui.ch_Controla_Estoque.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Produtos.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)   # ← correção

    def _estado_edicao(self):
        """Edição liberada: formulário + Salvar/Excluir/Limpar ativos."""
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave; não muda
        self.ui.txt_Descricao.setEnabled(True)
        self.ui.txt_Peso.setEnabled(True)
        self.ui.txt_Custo.setEnabled(True)
        self.ui.ch_Mat_Prima.setEnabled(True)
        self.ui.ch_Prod_Acabado.setEnabled(True)
        self.ui.ch_Mao_Obra.setEnabled(True)
        self.ui.ch_Controla_Estoque.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Produtos.setEnabled(False)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        """Converte exceções comuns em mensagens amigáveis."""
        nome = type(exc).__name__
        if nome == "UniqueViolation":
            return "Já existe um produto com esse código."
        if nome == "OperationalError":
            return "Falha de conexão com o banco de dados."
        return str(exc) or nome

    # ---------------- acoes de tela ----------------

    def _iniciar_novo(self, codigo: str = ""):
        """Entra no modo novo registro, preservando o código se informado."""
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        if codigo:
            self.ui.txt_Codigo.setText(codigo)
            self.ui.txt_Descricao.setFocus()
        else:
            self.ui.txt_Codigo.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return  # só permite novo no estado inicial
        self._iniciar_novo()

    def _liberar_edicao(self):
        """Botão Editar: libera os campos para alteração."""
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.txt_Descricao.setFocus()

    def _ao_enter_codigo(self):
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            self._pesquisar()  # campo vazio -> abre a tela de pesquisa
            return

        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de produtos indisponível.")
            return

        try:
            produto = self._service.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar produto por código")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o produto:\n{self._mensagem_erro(exc)}")
            return

        if produto:
            self._preencher(produto)
            return

        resposta = QMessageBox.question(
            self, "Produto não encontrado",
            f"Nenhum produto com o código '{codigo}'.\n\n"
            "Deseja cadastrar um novo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._iniciar_novo(codigo)

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

    def _validar_obrigatorios(self) -> bool:
        codigo = self.ui.txt_Codigo.text().strip()
        descricao = self.ui.txt_Descricao.text().strip()

        if not codigo:
            QMessageBox.warning(
                self, "Atenção", "Informe o código do produto.")
            self.ui.txt_Codigo.setFocus()
            return False

        if not descricao:
            QMessageBox.warning(
                self, "Atenção", "Informe a descrição do produto.")
            self.ui.txt_Descricao.setFocus()
            return False

        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de produtos indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                self._service.salvar(dados)
            elif self._modo == ESTADO_EDICAO:
                self._service.atualizar(dados)
            else:
                return  # estado não permite salvar
        except Exception as exc:
            logger.exception("Falha ao salvar produto")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o produto:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Produto salvo")
        QMessageBox.information(
            self, "Sucesso", "Produto salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de produtos indisponível.")
            return

        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            QMessageBox.warning(
                self, "Atenção", "Informe o código do produto a excluir.")
            self.ui.txt_Codigo.setFocus()
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir o produto '{codigo}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir produto")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir o produto:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Produto excluído: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Produto excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

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
        self._modo = ESTADO_INICIAL
        self._codigo_original = None
        self._estado_inicial()

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
        self._codigo_original = produto.codigo
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
