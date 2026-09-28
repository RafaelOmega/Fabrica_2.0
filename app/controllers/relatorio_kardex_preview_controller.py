# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de kardex.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
Aberta pelo botão Filtrar da tela de kardex.

O QTextBrowser usa folha de estilo própria (fundo branco, "papel"),
pois o tema escuro global do sistema torna o HTML claro ilegível.
"""
from datetime import datetime

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

from app.models.relatorio_kardex import KardexProduto
from app.reports.relatorio_kardex_pdf import _data_iso, _numero
from app.utils.logger import get_logger
from app.views.ui_relatorio_kardex_preview import Ui_Rel_Kardex_Preview

logger = get_logger("relatorio_kardex_preview")

AZUL = "#1F3B5B"
ZEBRA = "#F2F5F8"
LINHA = "#C9D3DE"
CINZA = "#5A6B7B"
TEXTO = "#222222"

# "Papel" do preview: fundo branco fixo, independente do tema escuro global
_ESTILO_PAPEL = f"""
QTextBrowser {{
    background-color: #FFFFFF;
    color: {TEXTO};
    border: 1px solid {LINHA};
}}
"""


class RelKardexPreviewController(QDialog):
    """Pré-visualização do kardex + exportação (PDF/XLSX/CSV)."""

    def __init__(self, kardex_list: list[KardexProduto], periodo: str,
                 parent=None):
        super().__init__(parent)
        self._kardex_list = kardex_list
        self._periodo = periodo

        self.ui = Ui_Rel_Kardex_Preview()
        self.ui.setupUi(self)

        self.ui.txt_Visualizacao.setStyleSheet(_ESTILO_PAPEL)

        self.ui.bt_PDF.clicked.connect(self._gerar_pdf)
        self.ui.bt_XLSX.clicked.connect(self._gerar_xlsx)
        self.ui.bt_CSV.clicked.connect(self._gerar_csv)
        self.ui.bt_Fechar.clicked.connect(self.accept)

        self._montar_visualizacao()

    # ---------------- visualização (mesmo layout do PDF) ----------------

    def _montar_visualizacao(self):
        partes = [
            f"<h2 style='color:{AZUL};margin-bottom:2px;'>"
            "RELATÓRIO DE KARDEX DO PRODUTO</h2>",
        ]
        if self._periodo:
            partes.append(f"<p style='color:{CINZA};'>{self._periodo}</p>")
        if not self._kardex_list:
            partes.append(
                "<p>Nenhum produto com movimentação no período.</p>")
        for kardex in self._kardex_list:
            partes.append(self._html_produto(kardex))
        self.ui.txt_Visualizacao.setHtml("".join(partes))

    @staticmethod
    def _html_produto(kardex: KardexProduto) -> str:
        html = [
            "<table width='100%' cellspacing='0' cellpadding='0'>"
            f"<tr><td style='background-color:{AZUL};color:#FFFFFF;"
            "padding:6px 8px;font-size:10pt;'>"
            f"<b>Produto {kardex.codigo}</b> · {kardex.descricao}"
            "</td></tr></table>",
            f"<p style='color:{CINZA};'>Saldo inicial: "
            f"<b>{_numero(kardex.saldo_inicial)}</b> kg</p>",
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};'>",
            f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
            "<th align='left'>Data</th><th align='left'>Documento</th>"
            "<th align='left'>Histórico</th>"
            "<th align='right'>Entrada</th><th align='right'>Saída</th>"
            "<th align='right'>Saldo</th></tr>",
        ]
        if kardex.movimentos:
            for indice, movimento in enumerate(kardex.movimentos):
                fundo = ZEBRA if indice % 2 else "#FFFFFF"
                html.append(
                    f"<tr style='background-color:{fundo};'>"
                    f"<td>{_data_iso(movimento.data)}</td>"
                    f"<td>{movimento.documento}</td>"
                    f"<td>{movimento.historico}</td>"
                    f"<td align='right'>"
                    f"{_numero(movimento.entrada) if movimento.entrada else '—'}</td>"
                    f"<td align='right'>"
                    f"{_numero(movimento.saida) if movimento.saida else '—'}</td>"
                    f"<td align='right'>{_numero(movimento.saldo)}</td>"
                    "</tr>")
        else:
            html.append("<tr><td>—</td><td>—</td>"
                        "<td>sem movimentos no período</td><td>—</td>"
                        "<td>—</td>"
                        f"<td align='right'>{_numero(kardex.saldo_inicial)}</td>"
                        "</tr>")
        html.append(
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='3'>Saldo final</td>"
            f"<td align='right'>{_numero(kardex.entradas_total)}</td>"
            f"<td align='right'>{_numero(kardex.saidas_total)}</td>"
            f"<td align='right'>{_numero(kardex.saldo_final)}</td></tr>"
            "</table><br>")
        return "".join(html)

    # ---------------- exportação ----------------

    def _gerar_pdf(self):
        from app.reports.relatorio_kardex_pdf import gerar_pdf_kardex
        self._exportar("PDF (*.pdf)", gerar_pdf_kardex)

    def _gerar_xlsx(self):
        from app.reports.relatorio_kardex_export import gerar_xlsx_kardex
        self._exportar("Excel (*.xlsx)", gerar_xlsx_kardex)

    def _gerar_csv(self):
        from app.reports.relatorio_kardex_export import gerar_csv_kardex
        self._exportar("CSV (*.csv)", gerar_csv_kardex)

    def _exportar(self, filtro_arquivo, funcao):
        sugerido = f"Relatorio_Kardex_{datetime.now():%Y-%m-%d}"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", sugerido, filtro_arquivo)
        if not caminho:
            return
        try:
            funcao(self._kardex_list, caminho, periodo=self._periodo)
        except Exception as exc:
            QMessageBox.critical(
                self, "Relatório", f"Erro ao gerar o arquivo:\n{exc}")
            return
        logger.info("Arquivo gerado: %s", caminho)
        QMessageBox.information(
            self, "Relatório", f"Arquivo gerado com sucesso:\n{caminho}")
