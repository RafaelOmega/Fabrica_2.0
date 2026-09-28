# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de estoque geral.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
Aberta pelo botão Filtrar da tela de estoque geral.

O QTextBrowser usa folha de estilo própria (fundo branco, "papel"),
pois o tema escuro global do sistema torna o HTML claro ilegível.
"""
from datetime import datetime

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from app.models.relatorio_estoque_geral import LinhaEstoqueGeral
from app.reports.relatorio_estoque_geral_export import (
    gerar_csv_estoque_geral,
    gerar_xlsx_estoque_geral,
)
from app.reports.relatorio_estoque_geral_pdf import (
    _moeda,
    _numero,
    gerar_pdf_estoque_geral,
)
from app.utils.logger import get_logger
from app.views.ui_relatorio_estoque_geral_preview import (
    Ui_Rel_Estoque_Geral_Preview,
)

logger = get_logger("relatorio_estoque_geral_preview")

AZUL = "#1F3B5B"
ZEBRA = "#F2F5F8"
TOTAL = "#E8EDF2"

_TD = "padding:4px 6px;font-size:9pt;border-bottom:1px solid #E5E9EF;"


class RelEstoqueGeralPreviewController(QDialog):
    """Diálogo de pré-visualização com exportação PDF/XLSX/CSV."""

    def __init__(self, linhas: list[LinhaEstoqueGeral], periodo: str,
                 parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Estoque_Geral_Preview()
        self.ui.setupUi(self)
        self._linhas = linhas
        self._periodo = periodo

        # "papel": fundo branco para o HTML claro ficar legível
        self.ui.txt_Visualizacao.setStyleSheet(
            "QTextBrowser { background-color:#FFFFFF; color:#1F2937; }")

        self.ui.bt_PDF.clicked.connect(self._gerar_pdf)
        self.ui.bt_XLSX.clicked.connect(self._gerar_xlsx)
        self.ui.bt_CSV.clicked.connect(self._gerar_csv)
        self.ui.bt_Fechar.clicked.connect(self.reject)

        self.ui.txt_Visualizacao.setHtml(self._html())

    # ---------------- html ----------------

    def _html(self) -> str:
        html = [
            "<html><body>",
            f"<div style='background-color:{AZUL};color:#FFFFFF;"
            "padding:8px;font-size:12pt;'>"
            "<b>RELATÓRIO DE ESTOQUE GERAL</b></div>",
            f"<p style='color:#5A6B7B;font-size:9pt;'>{self._periodo} · "
            f"Emitido em {datetime.now():%d/%m/%Y %H:%M}</p>",
            "<table width='100%' cellspacing='0'>",
            "<tr>"
            f"<th style='background-color:{AZUL};color:#FFFFFF;"
            "padding:5px 6px;font-size:9pt;text-align:left;'>Produto</th>"
            f"<th style='background-color:{AZUL};color:#FFFFFF;"
            "padding:5px 6px;font-size:9pt;' align='right'>Entradas</th>"
            f"<th style='background-color:{AZUL};color:#FFFFFF;"
            "padding:5px 6px;font-size:9pt;' align='right'>Saídas</th>"
            f"<th style='background-color:{AZUL};color:#FFFFFF;"
            "padding:5px 6px;font-size:9pt;' align='right'>Saldo</th>"
            f"<th style='background-color:{AZUL};color:#FFFFFF;"
            "padding:5px 6px;font-size:9pt;' align='right'>Custo Unit.</th>"
            f"<th style='background-color:{AZUL};color:#FFFFFF;"
            "padding:5px 6px;font-size:9pt;' align='right'>"
            "Valor em Estoque</th></tr>",
        ]
        if not self._linhas:
            html.append(
                f"<tr><td colspan='6' style='{_TD}'>"
                "Nenhum produto com movimentação até a data final.</td></tr>")
        for indice, linha in enumerate(self._linhas):
            fundo = ZEBRA if indice % 2 else "#FFFFFF"
            html.append(
                f"<tr style='background-color:{fundo};'>"
                f"<td style='{_TD}'>{linha.codigo} · {linha.descricao}</td>"
                f"<td style='{_TD}' align='right'>"
                f"{_numero(linha.entradas)}</td>"
                f"<td style='{_TD}' align='right'>"
                f"{_numero(linha.saidas)}</td>"
                f"<td style='{_TD}' align='right'>"
                f"{_numero(linha.saldo)}</td>"
                f"<td style='{_TD}' align='right'>"
                f"{_moeda(linha.custo_unitario)}</td>"
                f"<td style='{_TD}' align='right'>"
                f"{_moeda(linha.valor_estoque)}</td></tr>")
        html.append(
            f"<tr style='background-color:{TOTAL};'>"
            f"<td style='{_TD}'><b>Total geral</b></td>"
            f"<td style='{_TD}' align='right'><b>"
            f"{_numero(sum(l.entradas for l in self._linhas))}</b></td>"
            f"<td style='{_TD}' align='right'><b>"
            f"{_numero(sum(l.saidas for l in self._linhas))}</b></td>"
            f"<td style='{_TD}' align='right'>—</td>"
            f"<td style='{_TD}' align='right'>—</td>"
            f"<td style='{_TD}' align='right'><b>"
            f"{_moeda(sum(l.valor_estoque for l in self._linhas))}</b></td>"
            "</tr>")
        html.append("</table></body></html>")
        return "".join(html)

    # ---------------- exportações ----------------

    def _gerar_pdf(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", "relatorio_estoque_geral.pdf", "PDF (*.pdf)")
        if not caminho:
            return
        try:
            gerar_pdf_estoque_geral(self._linhas, caminho, self._periodo)
        except Exception as exc:
            logger.exception("Falha ao gerar PDF")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível gerar o PDF:\n{exc}")
            return
        QMessageBox.information(self, "Sucesso", f"PDF gerado:\n{caminho}")

    def _gerar_xlsx(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar XLSX", "relatorio_estoque_geral.xlsx",
            "Excel (*.xlsx)")
        if not caminho:
            return
        try:
            gerar_xlsx_estoque_geral(self._linhas, caminho, self._periodo)
        except Exception as exc:
            logger.exception("Falha ao gerar XLSX")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível gerar o XLSX:\n{exc}")
            return
        QMessageBox.information(self, "Sucesso", f"XLSX gerado:\n{caminho}")

    def _gerar_csv(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar CSV", "relatorio_estoque_geral.csv", "CSV (*.csv)")
        if not caminho:
            return
        try:
            gerar_csv_estoque_geral(self._linhas, caminho, self._periodo)
        except Exception as exc:
            logger.exception("Falha ao gerar CSV")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível gerar o CSV:\n{exc}")
            return
        QMessageBox.information(self, "Sucesso", f"CSV gerado:\n{caminho}")
