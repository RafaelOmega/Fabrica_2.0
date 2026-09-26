# -*- coding: utf-8 -*-
"""Controller da tela de Entrada.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas aos services.

Fluxo (espelhado na Ficha Técnica):
  Inicial -> Novo (cabeçalho) -> [bt_Abrir_Itens] -> Itens
          -> [bt_Sair_Itens] -> Finalizado -> Salvar
"""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import (QKeySequence, QShortcut, QStandardItem,
                           QStandardItemModel)
from PySide6.QtWidgets import QMessageBox, QWidget

from app.models.entrada import Entrada, ItemEntrada
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_entrada import Ui_Entrada

try:
    from app.services.entrada_service import EntradaService
except ImportError:
    EntradaService = None

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None

try:
    from app.services.motivo_entrada_service import MotivoEntradaService
except ImportError:
    MotivoEntradaService = None

logger = get_logger("entrada")

# modos
MODO_INICIAL = "inicial"
MODO_NOVO = "novo"
MODO_VISUALIZACAO = "visualizacao"
MODO_EDICAO = "edicao"

# fases dentro de novo/edição
FASE_CABECALHO = "cabecalho"
FASE_ITENS = "itens"
FASE_FINALIZADO = "finalizado"

COLUNAS_ITENS = ["Código", "Insumo", "Qtde", "Custo", "Total"]


def _moeda(valor: float) -> str:
    """Formata valor no padrão monetário brasileiro: R$ 1.234,56."""
    texto = f"{valor:,.2f}"  # 1,234.56 (padrão US)
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class EntradaController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Entrada()
        self.ui.setupUi(self)

        self._service = EntradaService() if EntradaService else None
        self._service_produto = ProdutoService() if ProdutoService else None
        self._service_motivo = (
            MotivoEntradaService() if MotivoEntradaService else None)
        if self._service is None:
            logger.warning("EntradaService nao encontrado")
        if self._service_produto is None:
            logger.warning("ProdutoService nao encontrado")
        if self._service_motivo is None:
            logger.warning("MotivoEntradaService nao encontrado")

        self._modo = MODO_INICIAL
        self._fase = FASE_CABECALHO
        self._itens: list[ItemEntrada] = []
        self._produto_selecionado = None
        self._motivos: list = []
        self._entrada_id = None

        self._montar_tabela()
        self._carregar_motivos()
        self._conectar_botoes()
        self._conectar_teclas()
        self._limpar_campos()

    # ---------------- tabela ----------------

    def _montar_tabela(self):
        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS_ITENS)
        self.ui.tb_Itens.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Itens, coluna_stretch=1)

    def _carregar_motivos(self):
        self.ui.cmb_Motivo.clear()
        self._motivos = []
        if self._service_motivo is None:
            return
        try:
            self._motivos = self._service_motivo.pesquisar()
        except Exception:
            logger.exception("Falha ao carregar motivos")
            return
        self.ui.cmb_Motivo.addItem("-- Selecione --", userData=None)
        for motivo in self._motivos:
            self.ui.cmb_Motivo.addItem(
                f"{motivo.codigo} - {motivo.descricao}",
                userData=motivo.codigo,
            )

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisa_Entrada.clicked.connect(self._pesquisar)
        self.ui.bt_Abrir_Itens.clicked.connect(self._abrir_itens)
        self.ui.bt_Pesquisa_Itens.clicked.connect(self._pesquisar_insumo)
        self.ui.bt_Salvar_Itens.clicked.connect(self._adicionar_item)
        self.ui.bt_Limpar_Itens.clicked.connect(self._limpar_itens)
        self.ui.bt_Excluir_Itens.clicked.connect(self._excluir_item)
        self.ui.bt_Sair_Itens.clicked.connect(self._sair_itens)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        self.ui.txt_Sequencia.returnPressed.connect(self._ao_enter_sequencia)
        self.ui.txt_Cod_Prod.returnPressed.connect(self._buscar_insumo)
        self.ui.txt_Qtde.returnPressed.connect(
            lambda: self.ui.txt_Custo.setFocus())
        self.ui.txt_Custo.returnPressed.connect(self._adicionar_item)
        self.ui.cmb_Motivo.currentIndexChanged.connect(self._ao_mudar_motivo)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _aplicar_estado(self):
        """Aplica habilitação dos widgets conforme modo + fase."""
        m, f = self._modo, self._fase

        # ---- estado inicial ----
        if m == MODO_INICIAL:
            self.ui.txt_Sequencia.setEnabled(True)
            self.ui.bt_Pesquisa_Entrada.setEnabled(True)
            self.ui.bt_Novo.setEnabled(True)
            self._set_formulario(False)
            self.ui.bt_Abrir_Itens.setEnabled(False)
            self.ui.bt_Sair_Itens.setEnabled(False)
            self._set_crud(salvar=False, editar=False,
                           excluir=False, limpar=False)
            return

        # ---- visualização ----
        if m == MODO_VISUALIZACAO:
            self.ui.txt_Sequencia.setEnabled(False)
            self.ui.bt_Pesquisa_Entrada.setEnabled(False)
            self.ui.bt_Novo.setEnabled(False)
            self._set_formulario(False)
            self.ui.bt_Abrir_Itens.setEnabled(False)
            self.ui.bt_Sair_Itens.setEnabled(False)
            self._set_crud(salvar=False, editar=True,
                           excluir=True, limpar=True)
            return

        # ---- novo / edição ----
        self.ui.txt_Sequencia.setEnabled(False)
        self.ui.bt_Pesquisa_Entrada.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        cabecalho_ativo = (f == FASE_CABECALHO)
        itens_ativo = (f == FASE_ITENS)

        # cabeçalho
        self.ui.dt_Entrada.setEnabled(cabecalho_ativo)
        self.ui.cmb_Motivo.setEnabled(cabecalho_ativo)

        # bt_Abrir_Itens: ativo no cabeçalho e no finalizado (reabrir)
        self.ui.bt_Abrir_Itens.setEnabled(
            cabecalho_ativo or f == FASE_FINALIZADO)

        # itens
        self.ui.txt_Cod_Prod.setEnabled(itens_ativo)
        self.ui.bt_Pesquisa_Itens.setEnabled(itens_ativo)
        self.ui.txt_Qtde.setEnabled(itens_ativo)
        self.ui.txt_Custo.setEnabled(itens_ativo)
        self.ui.bt_Salvar_Itens.setEnabled(itens_ativo)
        self.ui.bt_Limpar_Itens.setEnabled(itens_ativo)
        self.ui.bt_Excluir_Itens.setEnabled(itens_ativo)
        self.ui.bt_Sair_Itens.setEnabled(itens_ativo)

        # salvar só no finalizado
        self._set_crud(
            salvar=(f == FASE_FINALIZADO),
            editar=False,
            excluir=(m == MODO_EDICAO),
            limpar=True,
        )

    def _set_formulario(self, ativo: bool):
        for w in (self.ui.dt_Entrada, self.ui.cmb_Motivo,
                  self.ui.txt_Cod_Prod, self.ui.bt_Pesquisa_Itens,
                  self.ui.txt_Qtde, self.ui.txt_Custo,
                  self.ui.bt_Salvar_Itens, self.ui.bt_Limpar_Itens,
                  self.ui.bt_Excluir_Itens):
            w.setEnabled(ativo)

    def _set_crud(self, salvar: bool, editar: bool,
                  excluir: bool, limpar: bool):
        self.ui.bt_Salvar.setEnabled(salvar)
        self.ui.bt_Editar.setEnabled(editar)
        self.ui.bt_Excluir.setEnabled(excluir)
        self.ui.bt_Limpar.setEnabled(limpar)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        nome = type(exc).__name__
        if nome == "ForeignKeyViolation":
            return "Registro relacionado não existe (motivo/produto)."
        if nome == "OperationalError":
            return "Falha de conexão com o banco de dados."
        return str(exc) or nome

    # ---------------- fluxo da entrada ----------------

    def _novo(self):
        if self._modo != MODO_INICIAL:
            return
        self._limpar_campos()
        self._modo = MODO_NOVO
        self._fase = FASE_CABECALHO
        self._aplicar_estado()
        self.ui.cmb_Motivo.setFocus()

    def _liberar_edicao(self):
        if self._modo != MODO_VISUALIZACAO:
            return
        self._modo = MODO_EDICAO
        self._fase = FASE_CABECALHO
        self._aplicar_estado()
        self.ui.cmb_Motivo.setFocus()

    def _abrir_itens(self):
        """bt_Abrir_Itens: valida o cabeçalho e libera a inclusão de itens."""
        if self._fase not in (FASE_CABECALHO, FASE_FINALIZADO):
            return
        if self._modo not in (MODO_NOVO, MODO_EDICAO):
            return
        if self.ui.cmb_Motivo.currentData() is None:
            QMessageBox.warning(
                self, "Atenção", "Selecione o motivo da entrada.")
            self.ui.cmb_Motivo.setFocus()
            return

        self._fase = FASE_ITENS
        self._aplicar_estado()
        self.ui.txt_Cod_Prod.setFocus()

    def _sair_itens(self):
        """bt_Sair_Itens: finaliza a inclusão de itens e libera o Salvar."""
        if self._fase != FASE_ITENS:
            return
        self._fase = FASE_FINALIZADO
        self._aplicar_estado()
        self.ui.bt_Salvar.setFocus()

    def _ao_enter_sequencia(self):
        texto = self.ui.txt_Sequencia.text().strip()
        if not texto:
            self._pesquisar()
            return

        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de entradas indisponível.")
            return

        if not texto.isdigit():
            QMessageBox.warning(
                self, "Atenção", "A sequência é numérica.")
            return

        try:
            entrada = self._service.buscar_por_sequencia(int(texto))
        except Exception as exc:
            logger.exception("Falha ao buscar entrada")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar a entrada:\n{self._mensagem_erro(exc)}")
            return

        if entrada:
            self._preencher(entrada)
            return

        resposta = QMessageBox.question(
            self, "Entrada não encontrada",
            f"Nenhuma entrada com a sequência '{texto}'.\n\n"
            "Deseja cadastrar uma nova?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._novo()

    def _pesquisar(self):
        from app.controllers.pesquisa_entrada_controller import (
            PesquisaEntradaController,
        )
        try:
            dialogo = PesquisaEntradaController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            entrada = dialogo.entrada_selecionada()
            if entrada:
                self._preencher(entrada)

    # ---------------- motivo ----------------

    def _motivo_atual(self):
        codigo = self.ui.cmb_Motivo.currentData()
        if not codigo:
            return None
        for motivo in self._motivos:
            if motivo.codigo == codigo:
                return motivo
        return None

    def _ao_mudar_motivo(self):
        """Hook para o acionamento da produção.

        Quando o motivo selecionado tem baixa_producao=True (Produção),
        a produção será acionada aqui — junto dos campos de Milho,
        após os testes dos controles.
        """
        motivo = self._motivo_atual()
        if motivo and motivo.baixa_producao:
            logger.info("Motivo de produção selecionado: %s", motivo.codigo)
            # TODO: acionamento da produção (campos Milho 60KG)

    # ---------------- insumo / itens ----------------

    def _pesquisar_insumo(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._aplicar_insumo(produto)

    def _buscar_insumo(self):
        if self._fase != FASE_ITENS:
            return
        codigo = self.ui.txt_Cod_Prod.text().strip()
        if not codigo:
            self._pesquisar_insumo()
            return
        if self._service_produto is None:
            return
        try:
            produto = self._service_produto.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar insumo")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o produto:\n{self._mensagem_erro(exc)}")
            return
        if produto:
            self._aplicar_insumo(produto)
        else:
            QMessageBox.warning(
                self, "Atenção",
                f"Nenhum produto com o código '{codigo}'.")

    def _aplicar_insumo(self, produto):
        """Aceita qualquer produto cadastrado como insumo da entrada."""
        self._produto_selecionado = produto
        self.ui.txt_Cod_Prod.setText(produto.codigo)
        self.ui.txt_Descricao_Prod.setText(produto.descricao)
        self.ui.txt_Custo.setText(f"{produto.custo:.4f}".replace(".", ","))
        self.ui.txt_Qtde.setFocus()

    def _adicionar_item(self):
        if self._fase != FASE_ITENS:
            return
        produto = self._produto_selecionado
        if produto is None:
            QMessageBox.warning(
                self, "Atenção", "Informe o produto do item.")
            self.ui.txt_Cod_Prod.setFocus()
            return

        try:
            qtde = float(self.ui.txt_Qtde.text().strip().replace(",", "."))
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

        try:
            custo = float(
                self.ui.txt_Custo.text().strip().replace(",", ".") or 0)
        except ValueError:
            QMessageBox.warning(
                self, "Atenção", "Informe um custo válido.")
            self.ui.txt_Custo.setFocus()
            return
        if custo < 0:
            QMessageBox.warning(
                self, "Atenção", "O custo não pode ser negativo.")
            self.ui.txt_Custo.setFocus()
            return

        # se o produto já existe na entrada, atualiza qtde/custo
        for item in self._itens:
            if item.codigo_produto == produto.codigo:
                item.quantidade = qtde
                item.custo = custo
                break
        else:
            self._itens.append(ItemEntrada(
                produto_id=produto.id,
                codigo_produto=produto.codigo,
                quantidade=qtde,
                custo=custo,
            ))

        self._produto_selecionado = None
        self.ui.txt_Cod_Prod.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self.ui.txt_Custo.clear()
        self._atualizar_tabela()
        self.ui.txt_Cod_Prod.setFocus()

    def _excluir_item(self):
        if self._fase != FASE_ITENS:
            return
        indice = self.ui.tb_Itens.currentIndex()
        if not indice.isValid():
            QMessageBox.warning(
                self, "Atenção", "Selecione um item na tabela.")
            return
        del self._itens[indice.row()]
        self._atualizar_tabela()

    def _limpar_itens(self):
        if self._fase != FASE_ITENS:
            return
        resposta = QMessageBox.question(
            self, "Confirmar",
            "Remover todos os itens da entrada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        self._itens.clear()
        self._atualizar_tabela()

    def _atualizar_tabela(self):
        self._modelo.removeRows(0, self._modelo.rowCount())
        total = 0.0
        for item in self._itens:
            total += item.total
            self._modelo.appendRow([
                QStandardItem(item.codigo_produto),
                QStandardItem(self._descricao_de(item.codigo_produto)),
                QStandardItem(f"{item.quantidade:.4f}"),
                QStandardItem(_moeda(item.custo)),
                QStandardItem(_moeda(item.total)),
            ])
        self.ui.txt_Total_Itens.setText(_moeda(total))
        ajustar_larguras(self.ui.tb_Itens, coluna_stretch=1)

    def _produto_de(self, codigo: str):
        if self._service_produto is None:
            return None
        try:
            return self._service_produto.buscar_por_codigo(codigo)
        except Exception:
            return None

    def _descricao_de(self, codigo: str) -> str:
        produto = self._produto_de(codigo)
        return produto.descricao if produto else ""

    # ---------------- salvar / excluir ----------------

    def _validar_entrada(self) -> bool:
        if self.ui.cmb_Motivo.currentData() is None:
            QMessageBox.warning(
                self, "Atenção", "Selecione o motivo da entrada.")
            self.ui.cmb_Motivo.setFocus()
            return False
        if not self._itens:
            QMessageBox.warning(
                self, "Atenção", "Adicione pelo menos um item à entrada.")
            return False
        return True

    def _montar_entrada(self) -> Entrada:
        motivo = self._motivo_atual()
        return Entrada(
            id=self._entrada_id,
            motivo_id=motivo.id if motivo else None,
            data_entrada=self.ui.dt_Entrada.date().toString("yyyy-MM-dd"),
            itens=list(self._itens),
        )

    def _salvar(self):
        if self._modo not in (MODO_NOVO, MODO_EDICAO):
            return
        if self._fase != FASE_FINALIZADO:
            QMessageBox.warning(
                self, "Atenção",
                "Finalize a inclusão dos itens (Sair Itens) antes de salvar.")
            return
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de entradas indisponível.")
            return
        if not self._validar_entrada():
            return

        entrada = self._montar_entrada()
        try:
            if self._modo == MODO_NOVO:
                entrada = self._service.salvar(entrada)
            else:
                self._service.atualizar(entrada)
        except Exception as exc:
            logger.exception("Falha ao salvar entrada")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar a entrada:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Entrada salva: id=%s", entrada.id)
        QMessageBox.information(
            self, "Sucesso",
            f"Entrada salva com sucesso. Sequência: {entrada.sequencia}")
        self._limpar_campos()
        self.ui.txt_Sequencia.setFocus()

    def _excluir(self):
        if self._service is None or self._entrada_id is None:
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir a entrada '{self._entrada_id}' e todos os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(self._entrada_id)
        except Exception as exc:
            logger.exception("Falha ao excluir entrada")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir a entrada:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Entrada excluída: id=%s", self._entrada_id)
        QMessageBox.information(
            self, "Sucesso", "Entrada excluída com sucesso.")
        self._limpar_campos()
        self.ui.txt_Sequencia.setFocus()

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Sequencia.clear()
        self.ui.dt_Entrada.setDate(QDate.currentDate())
        self.ui.cmb_Motivo.setCurrentIndex(0)
        self.ui.txt_Cod_Prod.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self.ui.txt_Custo.clear()
        self.ui.txt_Total_Itens.clear()
        self._itens.clear()
        self._produto_selecionado = None
        self._entrada_id = None
        self._atualizar_tabela()
        self._modo = MODO_INICIAL
        self._fase = FASE_CABECALHO
        self._aplicar_estado()

    def _preencher(self, entrada: Entrada):
        self._limpar_campos()
        self._entrada_id = entrada.id
        self.ui.txt_Sequencia.setText(str(entrada.sequencia or entrada.id))
        data = QDate.fromString(entrada.data_entrada, "yyyy-MM-dd")
        if data.isValid():
            self.ui.dt_Entrada.setDate(data)
        indice = self.ui.cmb_Motivo.findData(entrada.motivo_codigo)
        if indice >= 0:
            self.ui.cmb_Motivo.setCurrentIndex(indice)
        self._itens = list(entrada.itens)
        self._atualizar_tabela()
        self._modo = MODO_VISUALIZACAO
        self._fase = FASE_CABECALHO
        self._aplicar_estado()
