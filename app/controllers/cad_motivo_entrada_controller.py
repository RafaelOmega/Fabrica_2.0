# -*- coding: utf-8 -*-
"""Controller do cadastro de motivos de entrada.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao MotivoEntradaService.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.logger import get_logger
from app.views.ui_cad_motivo_entrada import Ui_Cad_Motivo_Entrada

try:
    from app.services.motivo_entrada_service import MotivoEntradaService
except ImportError:
    MotivoEntradaService = None

logger = get_logger("cad_motivo_entrada")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"


class CadMotivoEntradaController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Motivo_Entrada()
        self.ui.setupUi(self)

        self._service = MotivoEntradaService() if MotivoEntradaService else None
        if self._service is None:
            logger.warning(
                "MotivoEntradaService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL

        self._conectar_botoes()
        self._conectar_teclas()
        self._limpar_campos()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Motivo.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        self.ui.txt_Codigo.returnPressed.connect(self._ao_enter_codigo)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(True)
        self.ui.bt_Pesquisar_Motivo.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.txt_Descricao.setEnabled(False)
        self.ui.chk_Baixa_Ficha.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Codigo.setEnabled(True)
        self.ui.txt_Descricao.setEnabled(True)
        self.ui.chk_Baixa_Ficha.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Motivo.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Descricao.setEnabled(False)
        self.ui.chk_Baixa_Ficha.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Motivo.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self.ui.txt_Descricao.setEnabled(True)
        self.ui.chk_Baixa_Ficha.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Motivo.setEnabled(False)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        nome = type(exc).__name__
        if nome == "UniqueViolation":
            return "Já existe um motivo com esse código."
        if nome == "OperationalError":
            return "Falha de conexão com o banco de dados."
        return str(exc) or nome

    # ---------------- acoes de tela ----------------

    def _iniciar_novo(self, codigo: str = ""):
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
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.txt_Descricao.setFocus()

    def _ao_enter_codigo(self):
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            self._pesquisar()
            return

        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de motivos indisponível.")
            return

        try:
            motivo = self._service.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar motivo por código")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o motivo:\n{self._mensagem_erro(exc)}")
            return

        if motivo:
            self._preencher(motivo)
            return

        resposta = QMessageBox.question(
            self, "Motivo não encontrado",
            f"Nenhum motivo com o código '{codigo}'.\n\n"
            "Deseja cadastrar um novo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._iniciar_novo(codigo)

    def _pesquisar(self):
        from app.controllers.pesquisa_motivo_entrada_controller import (
            PesquisaMotivoEntradaController,
        )
        try:
            dialogo = PesquisaMotivoEntradaController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            motivo = dialogo.motivo_selecionado()
            if motivo:
                self._preencher(motivo)

    def _validar_obrigatorios(self) -> bool:
        codigo = self.ui.txt_Codigo.text().strip()
        descricao = self.ui.txt_Descricao.text().strip()

        if not codigo:
            QMessageBox.warning(
                self, "Atenção", "Informe o código do motivo.")
            self.ui.txt_Codigo.setFocus()
            return False

        if not descricao:
            QMessageBox.warning(
                self, "Atenção", "Informe a descrição do motivo.")
            self.ui.txt_Descricao.setFocus()
            return False

        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de motivos indisponível.")
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
                return
        except Exception as exc:
            logger.exception("Falha ao salvar motivo")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o motivo:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Motivo salvo")
        QMessageBox.information(
            self, "Sucesso", "Motivo salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de motivos indisponível.")
            return

        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            QMessageBox.warning(
                self, "Atenção", "Informe o código do motivo a excluir.")
            self.ui.txt_Codigo.setFocus()
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir o motivo '{codigo}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir motivo")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir o motivo:\n{self._mensagem_erro(exc)}")
            return

        logger.info("Motivo excluído: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Motivo excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()
        self.ui.chk_Baixa_Ficha.setChecked(False)
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "descricao": self.ui.txt_Descricao.text().strip(),
            "baixa_producao": self.ui.chk_Baixa_Ficha.isChecked(),
        }

    def _preencher(self, motivo):
        self._limpar_campos()
        self.ui.txt_Codigo.setText(motivo.codigo)
        self.ui.txt_Descricao.setText(motivo.descricao)
        self.ui.chk_Baixa_Ficha.setChecked(motivo.baixa_producao)
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
