# -*- coding: utf-8 -*-
"""Controller da tela de Saída.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas aos services.

Fluxo (espelhado na Entrada):
  Inicial -> Novo (data) -> [bt_Abrir_Itens] -> Itens
          -> [bt_Sair_Itens] -> Finalizado -> Salvar
"""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import (QKeySequence, QShortcut, QStandardItem,
                           QStandardItemModel)
from PySide6.QtWidgets import QMessageBox, QWidget

from app.models.saida import ItemSaida, ItemSaidaMaoObra, Saida
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.utils.erros import mensagem_erro
from app.views.ui_saida import Ui_Saida

try:
    from app.services.saida_service import SaidaService
except ImportError:
    SaidaService = None

try:
    from app.services.produto_service import ProdutoService
except ImportError:
    ProdutoService = None

logger = get_logger("saida")

MODO_INICIAL = "inicial"
MODO_NOVO = "novo"
MODO_VISUALIZACAO = "visualizacao"
MODO_EDICAO = "edicao"

FASE_CABECALHO = "cabecalho"
FASE_ITENS = "itens"
FASE_FINALIZADO = "finalizado"

COLUNAS_ITENS = ["Código", "Produto", "Qtde", "Custo", "Total"]
COLUNAS_MAO_OBRA = ["Código", "Mão de Obra", "Qtde", "Custo", "Total"]


def _moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero(valor: float) -> str:
    texto = f"{valor:,.4f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


class SaidaController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Saida()
        self.ui.setupUi(self)

        self._service = SaidaService() if SaidaService else None
        self._service_produto = ProdutoService() if ProdutoService else None
        if self._service is None:
            logger.warning("SaidaService nao encontrado")
        if self._service_produto is None:
            logger.warning("ProdutoService nao encontrado")

        self._modo = MODO_INICIAL
        self._fase = FASE_CABECALHO
        self._itens: list[ItemSaida] = []
        self._mao_obra: list[ItemSaidaMaoObra] = []
        self._produto_selecionado = None
        self._saida_id = None

        self._montar_tabela()
        self._montar_tabela_mao_obra()
        self._conectar_botoes()
        self._conectar_teclas()
        self._limpar_campos()

    # ---------------- tabelas ----------------

    def _montar_tabela(self):
        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS_ITENS)
        self.ui.tb_Itens.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Itens, coluna_stretch=1)

    def _montar_tabela_mao_obra(self):
        self._modelo_mao = QStandardItemModel(self)
        self._modelo_mao.setHorizontalHeaderLabels(COLUNAS_MAO_OBRA)
        self.ui.tb_Mao_Obra.setModel(self._modelo_mao)
        configurar_tabela(self.ui.tb_Mao_Obra, coluna_stretch=1)

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisa_Saida.clicked.connect(self._pesquisar)
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
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _aplicar_estado(self):
        m, f = self._modo, self._fase

        if m == MODO_INICIAL:
            self.ui.txt_Sequencia.setEnabled(True)
            self.ui.bt_Pesquisa_Saida.setEnabled(True)
            self.ui.bt_Novo.setEnabled(True)
            self._set_formulario(False)
            self.ui.bt_Abrir_Itens.setEnabled(False)
            self.ui.bt_Sair_Itens.setEnabled(False)
            self._set_crud(salvar=False, editar=False,
                           excluir=False, limpar=False)
            return

        if m == MODO_VISUALIZACAO:
            self.ui.txt_Sequencia.setEnabled(False)
            self.ui.bt_Pesquisa_Saida.setEnabled(False)
            self.ui.bt_Novo.setEnabled(False)
            self._set_formulario(False)
            self.ui.bt_Abrir_Itens.setEnabled(False)
            self.ui.bt_Sair_Itens.setEnabled(False)
            self._set_crud(salvar=False, editar=True,
                           excluir=True, limpar=True)
            return

        self.ui.txt_Sequencia.setEnabled(False)
        self.ui.bt_Pesquisa_Saida.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        cabecalho_ativo = (f == FASE_CABECALHO)
        itens_ativo = (f == FASE_ITENS)

        self.ui.dt_Saida.setEnabled(cabecalho_ativo)

        self.ui.bt_Abrir_Itens.setEnabled(
            cabecalho_ativo or f == FASE_FINALIZADO)

        self.ui.txt_Cod_Prod.setEnabled(itens_ativo)
        self.ui.bt_Pesquisa_Itens.setEnabled(itens_ativo)
        self.ui.txt_Qtde.setEnabled(itens_ativo)
        self.ui.txt_Custo.setEnabled(itens_ativo)
        self.ui.bt_Salvar_Itens.setEnabled(itens_ativo)
        self.ui.bt_Limpar_Itens.setEnabled(itens_ativo)
        self.ui.bt_Excluir_Itens.setEnabled(itens_ativo)
        self.ui.bt_Sair_Itens.setEnabled(itens_ativo)

        self._set_crud(
            salvar=(f == FASE_FINALIZADO),
            editar=False,
            excluir=(m == MODO_EDICAO),
            limpar=True,
        )

    def _set_formulario(self, ativo: bool):
        for w in (self.ui.dt_Saida,
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
        return mensagem_erro(exc, contexto="produto")

    # ---------------- fluxo da saída ----------------

    def _novo(self):
        if self._modo != MODO_INICIAL:
            return
        self._limpar_campos()
        self._modo = MODO_NOVO
        self._fase = FASE_CABECALHO
        self._aplicar_estado()
        self.ui.dt_Saida.setFocus()

    def _liberar_edicao(self):
        if self._modo != MODO_VISUALIZACAO:
            return
        self._modo = MODO_EDICAO
        self._fase = FASE_CABECALHO
        self._aplicar_estado()
        self.ui.dt_Saida.setFocus()

    def _abrir_itens(self):
        if self._fase not in (FASE_CABECALHO, FASE_FINALIZADO):
            return
        if self._modo not in (MODO_NOVO, MODO_EDICAO):
            return
        self._fase = FASE_ITENS
        self._aplicar_estado()
        self.ui.txt_Cod_Prod.setFocus()

    def _sair_itens(self):
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
                self, "Erro", "Service de saídas indisponível.")
            return
        if not texto.isdigit():
            QMessageBox.warning(
                self, "Atenção", "A sequência é numérica.")
            return
        try:
            saida = self._service.buscar_por_sequencia(int(texto))
        except Exception as exc:
            logger.exception("Falha ao buscar saída")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar a saída:\n{self._mensagem_erro(exc)}")
            return
        if saida:
            self._preencher(saida)
            return
        resposta = QMessageBox.question(
            self, "Saída não encontrada",
            f"Nenhuma saída com a sequência '{texto}'.\n\n"
            "Deseja cadastrar uma nova?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._novo()

    def _pesquisar(self):
        from app.controllers.pesquisa_saida_controller import (
            PesquisaSaidaController,
        )
        try:
            dialogo = PesquisaSaidaController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            saida = dialogo.saida_selecionada()
            if saida:
                self._preencher(saida)

    # ---------------- produto / itens ----------------

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
            logger.exception("Falha ao buscar produto")
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

        saldo = self._saldo_atual(produto.id)
        if qtde > saldo:
            resposta = QMessageBox.question(
                self, "Saldo insuficiente",
                f"'{produto.descricao}' tem saldo de {_numero(saldo)}.\n"
                f"A saída de {_numero(qtde)} deixará o estoque negativo.\n\n"
                "Lançar mesmo assim?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if resposta != QMessageBox.StandardButton.Yes:
                return

        for item in self._itens:
            if item.codigo_produto == produto.codigo:
                item.quantidade = qtde
                item.custo = custo
                item.descricao_produto = produto.descricao
                break
        else:
            self._itens.append(ItemSaida(
                produto_id=produto.id,
                codigo_produto=produto.codigo,
                descricao_produto=produto.descricao,
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

    def _saldo_atual(self, produto_id: int | None) -> float:
        if produto_id is None or self._service is None:
            return float("inf")
        try:
            return self._service.saldo_atual(produto_id)
        except Exception:
            logger.exception("Falha ao consultar saldo do produto")
            return float("inf")

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
            "Remover todos os itens da saída?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        self._itens.clear()
        self._atualizar_tabela()

    # ---------------- mão de obra ----------------

    def _ficha_por_produto(self, produto_id: int | None):
        if produto_id is None or self._service is None:
            return None
        try:
            return self._service.buscar_ficha_produto(produto_id)
        except Exception:
            logger.exception("Falha ao buscar ficha do produto")
            return None

    def _recalcular_mao_obra(self):
        """Recomputa a mão de obra a partir dos itens acabados da saída.

        A quantidade é proporcional à quantidade vendida: cada item da
        ficha com mao_obra=true gera qtd = quantidade_kg * (vendida / sacos_batida).
        """
        self._mao_obra.clear()
        self._modelo_mao.removeRows(0, self._modelo_mao.rowCount())
        total_mao = 0.0
        for item in self._itens:
            ficha = self._ficha_por_produto(item.produto_id)
            if ficha is None or ficha.sacos_batida <= 0:
                continue
            proporcao = item.quantidade / ficha.sacos_batida
            for fi in ficha.itens:
                if not fi.mao_obra or fi.produto_id is None:
                    continue
                qtd = round(fi.quantidade_kg * proporcao, 4)
                custo = fi.custo
                for mo in self._mao_obra:
                    if mo.produto_id == fi.produto_id:
                        mo.quantidade += qtd
                        mo.custo = custo
                        break
                else:
                    self._mao_obra.append(ItemSaidaMaoObra(
                        produto_id=fi.produto_id,
                        codigo_produto=fi.codigo_produto,
                        descricao_produto=fi.descricao_produto or fi.codigo_produto,
                        quantidade=qtd,
                        custo=custo,
                    ))
        for mo in self._mao_obra:
            total_mao += mo.total
            self._modelo_mao.appendRow([
                QStandardItem(mo.codigo_produto),
                QStandardItem(mo.descricao_produto),
                QStandardItem(f"{mo.quantidade:.4f}"),
                QStandardItem(_moeda(mo.custo)),
                QStandardItem(_moeda(mo.total)),
            ])
        self.ui.txt_Total_Mao_Obra.setText(_moeda(total_mao))
        ajustar_larguras(self.ui.tb_Mao_Obra, coluna_stretch=1)

    def _atualizar_tabela(self):
        self._modelo.removeRows(0, self._modelo.rowCount())
        total = 0.0
        for item in self._itens:
            total += item.total
            self._modelo.appendRow([
                QStandardItem(item.codigo_produto),
                QStandardItem(item.descricao_produto),
                QStandardItem(f"{item.quantidade:.4f}"),
                QStandardItem(_moeda(item.custo)),
                QStandardItem(_moeda(item.total)),
            ])
        self.ui.txt_Total_Itens.setText(_moeda(total))
        ajustar_larguras(self.ui.tb_Itens, coluna_stretch=1)
        self._recalcular_mao_obra()

    # ---------------- salvar / excluir ----------------

    def _validar_saida(self) -> bool:
        if not self._itens:
            QMessageBox.warning(
                self, "Atenção", "Adicione pelo menos um item à saída.")
            return False
        return True

    def _montar_saida(self) -> Saida:
        return Saida(
            id=self._saida_id,
            data_saida=self.ui.dt_Saida.date().toString("yyyy-MM-dd"),
            itens=list(self._itens),
            mao_obra=list(self._mao_obra),
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
                self, "Erro", "Service de saídas indisponível.")
            return
        if not self._validar_saida():
            return

        saida = self._montar_saida()
        try:
            if self._modo == MODO_NOVO:
                saida = self._service.salvar(saida)
            else:
                self._service.atualizar(saida)
        except Exception as exc:
            logger.exception("Falha ao salvar saída")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar a saída:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Saída salva: id=%s", saida.id)
        QMessageBox.information(
            self, "Sucesso",
            f"Saída salva com sucesso. Sequência: {saida.sequencia}")
        self._limpar_campos()
        self.ui.txt_Sequencia.setFocus()

    def _excluir(self):
        if self._service is None or self._saida_id is None:
            return
        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir a saída '{self._saida_id}' e todos os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            self._service.excluir(self._saida_id)
        except Exception as exc:
            logger.exception("Falha ao excluir saída")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir a saída:\n{self._mensagem_erro(exc)}")
            return
        logger.info("Saída excluída: id=%s", self._saida_id)
        QMessageBox.information(
            self, "Sucesso", "Saída excluída com sucesso.")
        self._limpar_campos()
        self.ui.txt_Sequencia.setFocus()

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self._produto_selecionado = None
        self.ui.txt_Sequencia.clear()
        self.ui.dt_Saida.setDate(QDate.currentDate())
        self.ui.txt_Cod_Prod.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self.ui.txt_Custo.clear()
        self.ui.txt_Total_Itens.clear()
        self.ui.txt_Total_Mao_Obra.clear()
        self._itens.clear()
        self._mao_obra.clear()
        self._modelo_mao.removeRows(0, self._modelo_mao.rowCount())
        self._saida_id = None
        self._atualizar_tabela()
        self._modo = MODO_INICIAL
        self._fase = FASE_CABECALHO
        self._aplicar_estado()

    def _preencher(self, saida: Saida):
        self._limpar_campos()
        self._saida_id = saida.id
        self.ui.txt_Sequencia.setText(str(saida.sequencia or saida.id))
        data = QDate.fromString(saida.data_saida, "yyyy-MM-dd")
        if data.isValid():
            self.ui.dt_Saida.setDate(data)
        self._itens = list(saida.itens)
        self._mao_obra = list(saida.mao_obra)
        self._atualizar_tabela()
        self._modo = MODO_VISUALIZACAO
        self._fase = FASE_CABECALHO
        self._aplicar_estado()
