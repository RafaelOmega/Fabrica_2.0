# -*- coding: utf-8 -*-
"""Controller do cadastro de fichas técnicas.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao FichaTecnicaService e ProdutoService.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QStandardItem, QStandardItemModel, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.models.ficha_tecnica import FichaTecnica, ItemFichaTecnica
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_cad_ficha_tecnica import Ui_Ficha_Tecnica

try:
    from app.services.ficha_tecnica_service import FichaTecnicaService
except ImportError:
    FichaTecnicaService = None

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None

logger = get_logger("cad_ficha_tecnica")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"

COLUNAS_BATIDA = ["Código", "Matéria Prima", "Qtde Kg"]
COLUNAS_SACO = ["Código", "Matéria Prima", "Kg/Saco"]


class CadFichaTecnicaController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Ficha_Tecnica()
        self.ui.setupUi(self)

        self._service = FichaTecnicaService() if FichaTecnicaService else None
        self._service_produto = ProdutoService() if ProdutoService else None
        if self._service is None:
            logger.warning("FichaTecnicaService nao encontrado")
        if self._service_produto is None:
            logger.warning("ProdutoService nao encontrado")

        self._modo = ESTADO_INICIAL
        self._itens: list[ItemFichaTecnica] = []
        self._produto_selecionado = None  # mat-prima aguardando qtde

        self._montar_tabelas()
        self._conectar_botoes()
        self._conectar_teclas()
        self._limpar_campos()

    # ---------------- tabelas ----------------

    def _montar_tabelas(self):
        self._modelo_batida = QStandardItemModel(self)
        self._modelo_batida.setHorizontalHeaderLabels(COLUNAS_BATIDA)
        self.ui.tb_Itens_Batida.setModel(self._modelo_batida)
        configurar_tabela(self.ui.tb_Itens_Batida, coluna_stretch=1)

        self._modelo_saco = QStandardItemModel(self)
        self._modelo_saco.setHorizontalHeaderLabels(COLUNAS_SACO)
        self.ui.tb_Itens_Unitario.setModel(self._modelo_saco)
        configurar_tabela(self.ui.tb_Itens_Unitario, coluna_stretch=1,
                          selecionavel=False)

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisa_Ficha_Tecnica.clicked.connect(self._pesquisar)
        self.ui.bt_Abrir_Ficha.clicked.connect(self._ao_enter_ficha)
        self.ui.bt_Pesquisa_Prod_Acabado.clicked.connect(
            self._pesquisar_prod_acabado)
        self.ui.bt_Pesquisa_Mat_Prima.clicked.connect(
            self._pesquisar_mat_prima)
        self.ui.bt_Salvar_Itens.clicked.connect(self._adicionar_item)
        self.ui.bt_Limpar_Itens.clicked.connect(self._limpar_itens)
        self.ui.bt_Excluir_Itens.clicked.connect(self._excluir_item)
        self.ui.bt_Sair_Ficha.clicked.connect(self._limpar_campos)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        self.ui.txt_Ficha.returnPressed.connect(self._ao_enter_ficha)
        self.ui.txt_Cod_Mat_Prima.returnPressed.connect(self._buscar_mat_prima)
        self.ui.txt_Qtde.returnPressed.connect(self._adicionar_item)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Ficha.setEnabled(True)
        self.ui.bt_Pesquisa_Ficha_Tecnica.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        for w in (self.ui.txt_Sacos_Batida, self.ui.txt_Prod_Acabado,
                  self.ui.bt_Pesquisa_Prod_Acabado,
                  self.ui.txt_Cod_Mat_Prima, self.ui.bt_Pesquisa_Mat_Prima,
                  self.ui.txt_Qtde, self.ui.bt_Salvar_Itens,
                  self.ui.bt_Limpar_Itens, self.ui.bt_Excluir_Itens,
                  self.ui.bt_Salvar, self.ui.bt_Editar,
                  self.ui.bt_Excluir, self.ui.bt_Limpar,
                  self.ui.bt_Abrir_Ficha):
            w.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Ficha.setEnabled(False)  # id é gerado pelo banco
        for w in (self.ui.txt_Sacos_Batida, self.ui.txt_Prod_Acabado,
                  self.ui.bt_Pesquisa_Prod_Acabado,
                  self.ui.txt_Cod_Mat_Prima, self.ui.bt_Pesquisa_Mat_Prima,
                  self.ui.txt_Qtde, self.ui.bt_Salvar_Itens,
                  self.ui.bt_Limpar_Itens, self.ui.bt_Excluir_Itens,
                  self.ui.bt_Salvar, self.ui.bt_Limpar,
                  self.ui.bt_Abrir_Ficha):
            w.setEnabled(True)
        for w in (self.ui.bt_Editar, self.ui.bt_Excluir,
                  self.ui.bt_Novo, self.ui.bt_Pesquisa_Ficha_Tecnica):
            w.setEnabled(False)

    def _estado_visualizacao(self):
        for w in (self.ui.txt_Sacos_Batida, self.ui.txt_Prod_Acabado,
                  self.ui.bt_Pesquisa_Prod_Acabado,
                  self.ui.txt_Cod_Mat_Prima, self.ui.bt_Pesquisa_Mat_Prima,
                  self.ui.txt_Qtde, self.ui.bt_Salvar_Itens,
                  self.ui.bt_Limpar_Itens, self.ui.bt_Excluir_Itens,
                  self.ui.bt_Salvar, self.ui.bt_Novo,
                  self.ui.bt_Pesquisa_Ficha_Tecnica, self.ui.bt_Abrir_Ficha):
            w.setEnabled(False)
        for w in (self.ui.bt_Editar, self.ui.bt_Limpar, self.ui.bt_Excluir):
            w.setEnabled(True)

    def _estado_edicao(self):
        for w in (self.ui.txt_Sacos_Batida, self.ui.txt_Prod_Acabado,
                  self.ui.bt_Pesquisa_Prod_Acabado,
                  self.ui.txt_Cod_Mat_Prima, self.ui.bt_Pesquisa_Mat_Prima,
                  self.ui.txt_Qtde, self.ui.bt_Salvar_Itens,
                  self.ui.bt_Limpar_Itens, self.ui.bt_Excluir_Itens,
                  self.ui.bt_Salvar, self.ui.bt_Limpar,
                  self.ui.bt_Abrir_Ficha):
            w.setEnabled(True)
        for w in (self.ui.bt_Editar, self.ui.bt_Novo,
                  self.ui.bt_Pesquisa_Ficha_Tecnica):
            w.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(True)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        nome = type(exc).__name__
        if nome == "UniqueViolation":
            return "Já existe uma ficha para este produto."
        if nome == "OperationalError":
            return "Falha de conexão com o banco de dados."
        return str(exc) or nome

    # ---------------- fluxo da ficha ----------------

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self.ui.txt_Sacos_Batida.setFocus()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.txt_Sacos_Batida.setFocus()

    def _ao_enter_ficha(self):
        texto = self.ui.txt_Ficha.text().strip()
        if not texto:
            self._pesquisar()
            return

        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de fichas indisponível.")
            return

        if not texto.isdigit():
            QMessageBox.warning(
                self, "Atenção", "O código da ficha é numérico.")
            return

        try:
            ficha = self._service.buscar_por_id(int(texto))
        except Exception as exc:
            logger.exception("Falha ao buscar ficha")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar a ficha:\n{self._mensagem_erro(exc)}")
            return

        if ficha:
            self._preencher(ficha)
            return

        resposta = QMessageBox.question(
            self, "Ficha não encontrada",
            f"Nenhuma ficha com o código '{texto}'.\n\n"
            "Deseja cadastrar uma nova?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._novo()

    def _pesquisar(self):
        from app.controllers.pesquisa_ficha_tecnica_controller import (
            PesquisaFichaTecnicaController,
        )
        try:
            dialogo = PesquisaFichaTecnicaController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            ficha = dialogo.ficha_selecionada()
            if ficha:
                self._preencher(ficha)

    # ---------------- produto acabado / matéria prima ----------------

    def _pesquisar_prod_acabado(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._aplicar_prod_acabado(produto)

    def _aplicar_prod_acabado(self, produto):
        if not produto.prod_acabado:
            QMessageBox.warning(
                self, "Atenção",
                f"'{produto.codigo}' não é um produto acabado.")
            return
        self.ui.txt_Prod_Acabado.setText(produto.codigo)
        self.ui.txt_Descricao_Prod_Acabado.setText(produto.descricao)
        self._produto_acabado = produto
        self.ui.txt_Cod_Mat_Prima.setFocus()

    def _pesquisar_mat_prima(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._aplicar_mat_prima(produto)

    def _buscar_mat_prima(self):
        codigo = self.ui.txt_Cod_Mat_Prima.text().strip()
        if not codigo:
            self._pesquisar_mat_prima()
            return
        if self._service_produto is None:
            return
        try:
            produto = self._service_produto.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar matéria prima")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o produto:\n{self._mensagem_erro(exc)}")
            return
        if produto:
            self._aplicar_mat_prima(produto)
        else:
            QMessageBox.warning(
                self, "Atenção",
                f"Nenhum produto com o código '{codigo}'.")

    def _aplicar_mat_prima(self, produto):
        if not produto.mat_prima:
            QMessageBox.warning(
                self, "Atenção",
                f"'{produto.codigo}' não é matéria prima.")
            return
        self._produto_selecionado = produto
        self.ui.txt_Cod_Mat_Prima.setText(produto.codigo)
        self.ui.txt_Descricao_Prod.setText(produto.descricao)
        self.ui.txt_Qtde.setFocus()

    # ---------------- itens ----------------

    def _adicionar_item(self):
        produto = self._produto_selecionado
        if produto is None:
            QMessageBox.warning(
                self, "Atenção", "Informe a matéria prima do item.")
            self.ui.txt_Cod_Mat_Prima.setFocus()
            return

        texto = self.ui.txt_Qtde.text().strip().replace(",", ".")
        try:
            qtde = float(texto)
        except ValueError:
            QMessageBox.warning(
                self, "Atenção", "Informe uma quantidade válida.")
            self.ui.txt_Qtde.setFocus()
            return
        if qtde <= 0:
            QMessageBox.warning(
                self, "Atenção", "A quantidade deve ser maior que zero.")
            self.ui.txt_Qtde.setFocus()
            return

        # se o item já existe na ficha, atualiza a quantidade
        for item in self._itens:
            if item.codigo_produto == produto.codigo:
                item.quantidade_kg = qtde
                break
        else:
            self._itens.append(ItemFichaTecnica(
                produto_id=produto.id,
                codigo_produto=produto.codigo,
                quantidade_kg=qtde,
            ))

        self._produto_selecionado = None
        self.ui.txt_Cod_Mat_Prima.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self._atualizar_tabelas()
        self.ui.txt_Cod_Mat_Prima.setFocus()

    def _excluir_item(self):
        indice = self.ui.tb_Itens_Batida.currentIndex()
        if not indice.isValid():
            QMessageBox.warning(
                self, "Atenção", "Selecione um item na tabela Batida.")
            return
        del self._itens[indice.row()]
        self._atualizar_tabelas()

    def _limpar_itens(self):
        resposta = QMessageBox.question(
            self, "Confirmar",
            "Remover todos os itens da ficha?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        self._itens.clear()
        self._atualizar_tabelas()

    def _atualizar_tabelas(self):
        try:
            sacos = float(
                self.ui.txt_Sacos_Batida.text().strip().replace(",", ".") or 0)
        except ValueError:
            sacos = 0.0

        self._modelo_batida.removeRows(0, self._modelo_batida.rowCount())
        self._modelo_saco.removeRows(0, self._modelo_saco.rowCount())

        total_batida = 0.0
        for item in self._itens:
            total_batida += item.quantidade_kg
            self._modelo_batida.appendRow([
                QStandardItem(item.codigo_produto),
                QStandardItem(self._descricao_de(item.codigo_produto)),
                QStandardItem(f"{item.quantidade_kg:.4f}"),
            ])
            kg_saco = item.quantidade_kg / sacos if sacos > 0 else 0.0
            self._modelo_saco.appendRow([
                QStandardItem(item.codigo_produto),
                QStandardItem(self._descricao_de(item.codigo_produto)),
                QStandardItem(f"{kg_saco:.4f}"),
            ])

        self.ui.txt_Total_Batida.setText(f"{total_batida:.4f}")
        self.ui.txt_Total_Saco.setText(
            f"{total_batida / sacos:.4f}" if sacos > 0 else "0.0000")
        ajustar_larguras(self.ui.tb_Itens_Batida, coluna_stretch=1)
        ajustar_larguras(self.ui.tb_Itens_Unitario, coluna_stretch=1)

    def _descricao_de(self, codigo: str) -> str:
        if self._service_produto is None:
            return ""
        try:
            produto = self._service_produto.buscar_por_codigo(codigo)
            return produto.descricao if produto else ""
        except Exception:
            return ""

    # ---------------- salvar / excluir ----------------

    def _validar_ficha(self) -> bool:
        if not self.ui.txt_Prod_Acabado.text().strip():
            QMessageBox.warning(
                self, "Atenção", "Informe o produto acabado da ficha.")
            self.ui.txt_Prod_Acabado.setFocus()
            return False

        try:
            sacos = float(
                self.ui.txt_Sacos_Batida.text().strip().replace(",", "."))
        except ValueError:
            sacos = 0.0
        if sacos <= 0:
            QMessageBox.warning(
                self, "Atenção",
                "Informe a quantidade de sacos por batida (maior que zero).")
            self.ui.txt_Sacos_Batida.setFocus()
            return False

        if not self._itens:
            QMessageBox.warning(
                self, "Atenção", "Adicione pelo menos um item à ficha.")
            self.ui.txt_Cod_Mat_Prima.setFocus()
            return False

        return True

    def _montar_ficha(self) -> FichaTecnica:
        return FichaTecnica(
            id=self._ficha_id,
            produto_id=getattr(self, "_produto_acabado", None).id
            if getattr(self, "_produto_acabado", None) else None,
            codigo_produto=self.ui.txt_Prod_Acabado.text().strip(),
            sacos_batida=float(
                self.ui.txt_Sacos_Batida.text().strip().replace(",", ".")),
            itens=list(self._itens),
        )

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de fichas indisponível.")
            return
        if not self._validar_ficha():
            return

        ficha = self._montar_ficha()
        try:
            if self._modo == ESTADO_NOVO:
                ficha = self._service.salvar(ficha)
            elif self._modo == ESTADO_EDICAO:
                self._service.atualizar(ficha)
            else:
                return
        except Exception as exc:
            logger.exception("Falha ao salvar ficha")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar a ficha:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Ficha salva: id=%s", ficha.id)
        QMessageBox.information(
            self, "Sucesso",
            f"Ficha salva com sucesso. Código: {ficha.id}")
        self._limpar_campos()
        self.ui.txt_Ficha.setFocus()

    def _excluir(self):
        if self._service is None or self._ficha_id is None:
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir a ficha '{self._ficha_id}' e todos os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(self._ficha_id)
        except Exception as exc:
            logger.exception("Falha ao excluir ficha")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir a ficha:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Ficha excluída: id=%s", self._ficha_id)
        QMessageBox.information(
            self, "Sucesso", "Ficha excluída com sucesso.")
        self._limpar_campos()
        self.ui.txt_Ficha.setFocus()

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Ficha.clear()
        self.ui.txt_Sacos_Batida.clear()
        self.ui.txt_Prod_Acabado.clear()
        self.ui.txt_Descricao_Prod_Acabado.clear()
        self.ui.txt_Cod_Mat_Prima.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self.ui.txt_Total_Batida.clear()
        self.ui.txt_Total_Saco.clear()
        self._itens.clear()
        self._produto_selecionado = None
        self._ficha_id = None
        self._produto_acabado = None
        self._atualizar_tabelas()
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _preencher(self, ficha: FichaTecnica):
        self._limpar_campos()
        self._ficha_id = ficha.id
        self._produto_acabado = None
        self.ui.txt_Ficha.setText(str(ficha.id))
        self.ui.txt_Sacos_Batida.setText(f"{ficha.sacos_batida:.4f}")
        self.ui.txt_Prod_Acabado.setText(ficha.codigo_produto)
        self.ui.txt_Descricao_Prod_Acabado.setText(
            self._descricao_de(ficha.codigo_produto))
        self._itens = list(ficha.itens)
        self._atualizar_tabelas()
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
