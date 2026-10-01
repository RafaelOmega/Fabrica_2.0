# -*- coding: utf-8 -*-
"""Controller do cadastro de unidades de medida.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao UnidadeMedidaService.

O código é automático (gerado no salvar): o campo txt_Codigo é
somente leitura, exibindo o código da unidade carregada/salva.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_cad_unidade_medida import Ui_Cad_Unidade_Medida

try:
    from app.services.unidade_medida_service import UnidadeMedidaService
except ImportError:
    UnidadeMedidaService = None

logger = get_logger("cad_unidade_medida")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"


class CadUnidadeMedidaController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Unidade_Medida()
        self.ui.setupUi(self)

        self._service = (UnidadeMedidaService()
                         if UnidadeMedidaService else None)
        if self._service is None:
            logger.warning(
                "UnidadeMedidaService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL

        self._conectar_botoes()
        self._conectar_teclas()
        self._limpar_campos()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Unidade_Medida.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # código é automático: Enter no campo abre a pesquisa
        self.ui.txt_Codigo.returnPressed.connect(self._pesquisar)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.bt_Pesquisar_Unidade_Medida.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.txt_Descricao.setEnabled(False)
        self.ui.dsb_Fator.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.setEnabled(True)
        self.ui.dsb_Fator.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Unidade_Medida.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Descricao.setEnabled(False)
        self.ui.dsb_Fator.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Unidade_Medida.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self.ui.txt_Descricao.setEnabled(True)
        self.ui.dsb_Fator.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Unidade_Medida.setEnabled(False)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(
            exc, duplicidade="Já existe uma unidade com esse código.")

    # ---------------- acoes de tela ----------------

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self.ui.txt_Descricao.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.txt_Descricao.setFocus()

    def _pesquisar(self):
        from app.controllers.pesquisa_unidade_medida_controller import (
            PesquisaUnidadeMedidaController,
        )
        try:
            dialogo = PesquisaUnidadeMedidaController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            unidade = dialogo.unidade_selecionada()
            if unidade:
                self._preencher(unidade)

    def _validar_obrigatorios(self) -> bool:
        descricao = self.ui.txt_Descricao.text().strip()

        if not descricao:
            QMessageBox.warning(
                self, "Atenção", "Informe a descrição da unidade.")
            self.ui.txt_Descricao.setFocus()
            return False

        if float(self.ui.dsb_Fator.value()) <= 0:
            QMessageBox.warning(
                self, "Atenção",
                "Informe um fator de conversão maior que zero.")
            self.ui.dsb_Fator.setFocus()
            return False

        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de unidades indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                unidade = self._service.salvar(dados)
                # exibe o código gerado automaticamente
                self.ui.txt_Codigo.setText(unidade.codigo)
            elif self._modo == ESTADO_EDICAO:
                self._service.atualizar(dados)
            else:
                return
        except Exception as exc:
            logger.exception("Falha ao salvar unidade")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar a unidade:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Unidade salva")
        QMessageBox.information(
            self, "Sucesso", "Unidade salva com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de unidades indisponível.")
            return

        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            QMessageBox.warning(
                self, "Atenção", "Nenhuma unidade carregada para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir a unidade '{codigo}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir unidade")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir a unidade:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Unidade excluída: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Unidade excluída com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()
        self.ui.dsb_Fator.setValue(0.0)
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "descricao": self.ui.txt_Descricao.text().strip(),
            "fator_conversao": float(self.ui.dsb_Fator.value()),
        }

    def _preencher(self, unidade):
        self._limpar_campos()
        self.ui.txt_Codigo.setText(unidade.codigo)
        self.ui.txt_Descricao.setText(unidade.descricao)
        self.ui.dsb_Fator.setValue(unidade.fator_conversao)
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
