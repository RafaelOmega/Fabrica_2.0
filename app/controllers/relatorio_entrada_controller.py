# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Entradas.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via service.

Filtros:
  - Entrada e Produto vazios: relatório completo do período
  - Entrada filtrada: apenas a entrada selecionada
  - Produto filtrado: Entrada Completa (entradas inteiras que o
    contêm) ou Só o Produto (apenas as linhas do produto)
"""
from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_entrada_service import RelatorioEntradaService
from app.utils.logger import get_logger
from app.views.ui_relatorio_entrada import Ui_Rel_Entrada

logger = get_logger("relatorio_entrada")


class RelEntradaController(QWidget):
    """Tela de filtros do relatório de entradas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Entrada()
        self.ui.setupUi(self)

        self._service = RelatorioEntradaService()
        self._entrada_id = None
        self._produto_id = None

        # padrão: mês corrente
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(QDate(hoje.year(), hoje.month(), 1))
        self.ui.dt_Data_Final.setDate(hoje)

        # padrão do modo de produto: entrada completa
        self.ui.rb_Entrada_Completa.setChecked(True)

        self.ui.bt_Pesquisar_Entrada.clicked.connect(self._pesquisar_entrada)
        self.ui.bt_Pesquisar_Produto.clicked.connect(self._pesquisar_produto)
        self.ui.bt_Filtrar.clicked.connect(self._filtrar)
        self.ui.txt_Entrada.textChanged.connect(self._ao_mudar_entrada)
        self.ui.txt_Produto.textChanged.connect(self._ao_mudar_produto)

    # ---------------- entrada ----------------

    def _ao_mudar_entrada(self):
        """Limpar o campo manualmente cancela o filtro de entrada."""
        if not self.ui.txt_Entrada.text().strip():
            self._entrada_id = None

    def _pesquisar_entrada(self):
        from app.controllers.pesquisa_entrada_controller import (
            PesquisaEntradaController,
        )
        dialogo = PesquisaEntradaController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            entrada = dialogo.entrada_selecionada()
            if entrada:
                self._entrada_id = entrada.id
                # padrão dos outros relatórios: código - descrição
                self.ui.txt_Entrada.setText(
                    f"{entrada.sequencia} - {entrada.motivo_descricao}")

    # ---------------- produto ----------------

    def _ao_mudar_produto(self):
        """Limpar o campo manualmente cancela o filtro de produto."""
        if not self.ui.txt_Produto.text().strip():
            self._produto_id = None

    def _pesquisar_produto(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialogo = PesquisaProdutoController(self)
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            produto = dialogo.produto_selecionado()
            if produto:
                self._produto_id = produto.id
                # padrão dos outros relatórios: código - descrição
                self.ui.txt_Produto.setText(
                    f"{produto.codigo} - {produto.descricao}")

    # ---------------- filtro ----------------

    def _filtrar(self):
        data_inicial = self.ui.dt_Data_Inicial.date().toString("yyyy-MM-dd")
        data_final = self.ui.dt_Data_Final.date().toString("yyyy-MM-dd")
        if data_final < data_inicial:
            QMessageBox.warning(
                self, "Atenção",
                "A data final deve ser maior ou igual à data inicial.")
            self.ui.dt_Data_Final.setFocus()
            return

        so_produto = bool(
            self._produto_id and self.ui.rb_So_Produto.isChecked())
        try:
            relatorio = self._service.relatorio(
                date.fromisoformat(data_inicial),
                date.fromisoformat(data_final),
                self._entrada_id,
                self._produto_id,
                so_produto,
            )
        except Exception as exc:
            logger.exception("Falha ao gerar o relatório de entradas")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível gerar o relatório:\n{exc}")
            return

        if not relatorio.tem_dados:
            mensagem = ("Nenhuma entrada com o produto selecionado "
                        "no período."
                        if self._produto_id
                        else "Nenhuma entrada no período.")
            QMessageBox.information(self, "Relatório", mensagem)
            return

        if self._entrada_id:
            # entrada específica: a busca é por id, o período não se aplica
            periodo = f"Entrada: {self.ui.txt_Entrada.text().strip()}"
        else:
            periodo = (
                f"Período: {self.ui.dt_Data_Inicial.date().toString('dd/MM/yyyy')}"
                f" a {self.ui.dt_Data_Final.date().toString('dd/MM/yyyy')}"
            )
        if self._produto_id:
            periodo += f" · Produto: {self.ui.txt_Produto.text().strip()}"
            if so_produto:
                periodo += " (só o produto)"

        from app.controllers.relatorio_entrada_preview_controller import (
            RelEntradaPreviewController,
        )
        dialogo = RelEntradaPreviewController(relatorio, periodo, self)
        dialogo.exec()
