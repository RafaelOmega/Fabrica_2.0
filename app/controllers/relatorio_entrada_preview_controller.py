# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de entradas.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
"""
from datetime import datetime

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

from app.models.relatorio_entrada import RelatorioEntrada
from app.reports.relatorio_entrada_pdf import _data_br, _moeda, _numero
from app.utils.logger import get_logger
from app.views.ui_relatorio_entrada_preview import Ui_Rel_Entrada_Preview

logger = get_logger("relatorio_entrada_preview")

AZUL = "#1F3B5B"
ZEBRA = "#F2F5F8"
LINHA = "#C9D3DE"
CINZA = "#5A6B7B"
TEXTO = "#222222"

_ESTILO_PAPEL = f"""
QTextBrowser {{
    background-color: #FFFFFF;
    color: {TEXTO};
    border: 1px solid {LINHA};
}}
"""


class RelEntradaPreviewController(QDialog):
    """Pré-visualização das entradas + exportação (PDF/XLSX/CSV)."""

    def __init__(self, relatorio: RelatorioEntrada, periodo: str,
                 parent=None):
        super().__init__(parent)
        self._relatorio = relatorio
        self._periodo = periodo

        self.ui = Ui_Rel_Entrada_Preview()
        self.ui.setupUi(self)

        self.ui.txt_Visualizacao.setStyleSheet(_ESTILO_PAPEL)

        self.ui.bt_PDF.clicked.connect(self._gerar_pdf)
        self.ui.bt_XLSX.clicked.connect(self._gerar_xlsx)
        self.ui.bt_CSV.clicked.connect(self._gerar_csv)
        self.ui.bt_Fechar.clicked.connect(self.accept)

        self._montar_visualizacao()

    # ---------------- visualização ----------------

    def _montar_visualizacao(self):
        partes = [
            f"<h2 style='color:{AZUL};margin-bottom:2px;'>"
            "RELATÓRIO DE ENTRADAS</h2>",
        ]
        if self._periodo:
            partes.append(f"<p style='color:{CINZA};'>{self._periodo}</p>")
        if not self._relatorio.tem_dados:
            partes.append("<p>Nenhuma entrada no período.</p>")

        for linha in self._relatorio.linhas:
            partes.append(self._html_entrada(linha))
        partes.append(self._html_total_geral())
        self.ui.txt_Visualizacao.setHtml("".join(partes))

    @staticmethod
    def _html_entrada(entrada) -> str:
        titulo = (f"<b>ENTRADA Nº {entrada.sequencia}</b> · "
                  f"{_data_br(entrada.data_entrada)}")
        if entrada.motivo_descricao:
            titulo += f" · {entrada.motivo_descricao}"
        html = [
            "<table width='100%' cellspacing='0' cellpadding='0'>"
            f"<tr><td style='background-color:{AZUL};color:#FFFFFF;"
            "padding:6px 8px;font-size:10pt;'>"
            f"{titulo}</td></tr></table>",
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;"
            f"color:{TEXTO};margin-top:4px;'>",
            f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
            "<th align='left'>Código</th><th align='left'>Produto</th>"
            "<th align='right'>Qtde</th><th align='right'>Custo</th>"
            "<th align='right'>Total</th></tr>",
        ]
        if entrada.itens:
            for indice, item in enumerate(entrada.itens):
                fundo = ZEBRA if indice % 2 else "#FFFFFF"
                html.append(
                    f"<tr style='background-color:{fundo};'>"
                    f"<td>{item.codigo}</td><td>{item.descricao}</td>"
                    f"<td align='right'>{_numero(item.quantidade)}</td>"
                    f"<td align='right'>{_moeda(item.custo)}</td>"
                    f"<td align='right'>{_moeda(item.total)}</td></tr>"
                )
        else:
            html.append(
                "<tr><td colspan='5' style='color:#888888;'>"
                "sem itens lançados</td></tr>")
        html.append(
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='4'>Total da Entrada</td>"
            f"<td align='right'>{_moeda(entrada.total)}</td></tr>"
            "</table><br>"
        )
        return "".join(html)

    def _html_total_geral(self) -> str:
        return (
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};'>"
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='4'>TOTAL GERAL</td>"
            f"<td align='right'>{_moeda(self._relatorio.total_geral)}</td></tr>"
            "</table>"
        )

    # ---------------- exportação ----------------

    def _gerar_pdf(self):
        from app.reports.relatorio_entrada_pdf import gerar_pdf_entradas
        self._exportar("PDF (*.pdf)", gerar_pdf_entradas)

    def _gerar_xlsx(self):
        from app.reports.relatorio_entrada_export import gerar_xlsx_entradas
        self._exportar("Excel (*.xlsx)", gerar_xlsx_entradas)

    def _gerar_csv(self):
        from app.reports.relatorio_entrada_export import gerar_csv_entradas
        self._exportar("CSV (*.csv)", gerar_csv_entradas)

    def _exportar(self, filtro_arquivo, funcao):
        sugerido = f"Relatorio_Entradas_{datetime.now():%Y-%m-%d}"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", sugerido, filtro_arquivo)
        if not caminho:
            return
        try:
            funcao(self._relatorio, caminho, periodo=self._periodo)
        except Exception as exc:
            QMessageBox.critical(
                self, "Relatório", f"Erro ao gerar o arquivo:\n{exc}")
            return
        logger.info("Arquivo gerado: %s", caminho)
        QMessageBox.information(
            self, "Relatório", f"Arquivo gerado com sucesso:\n{caminho}")
