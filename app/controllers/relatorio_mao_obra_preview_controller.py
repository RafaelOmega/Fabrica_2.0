# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de mão de obra.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
"""
from datetime import datetime

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

from app.models.relatorio_mao_obra import RelatorioMaoObra
from app.reports.relatorio_mao_obra_pdf import _moeda, _numero, _data_br
from app.utils.logger import get_logger
from app.views.ui_relatorio_mao_obra_preview import Ui_Rel_Mao_Obra_Preview

logger = get_logger("relatorio_mao_obra_preview")

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


class RelMaoObraPreviewController(QDialog):
    """Pré-visualização da mão de obra + exportação (PDF/XLSX/CSV)."""

    def __init__(self, relatorio: RelatorioMaoObra, periodo: str,
                 parent=None):
        super().__init__(parent)
        self._relatorio = relatorio
        self._periodo = periodo

        self.ui = Ui_Rel_Mao_Obra_Preview()
        self.ui.setupUi(self)

        self.ui.txt_Visualizacao.setStyleSheet(_ESTILO_PAPEL)

        self.ui.bt_PDF.clicked.connect(self._gerar_pdf)
        self.ui.bt_XLSX.clicked.connect(self._gerar_xlsx)
        self.ui.bt_CSV.clicked.connect(self._gerar_csv)
        self.ui.bt_Fechar.clicked.connect(self.accept)

        self._montar_visualizacao()

    # ---------------- visualização ----------------

    def _saidas_agrupadas(self):
        """Agrupa as linhas por saída, preservando a ordem."""
        saidas = []
        indice = {}
        for linha in self._relatorio.linhas:
            chave = linha.saida_id
            if chave not in indice:
                indice[chave] = len(saidas)
                saidas.append({
                    "sequencia": linha.sequencia,
                    "data_saida": linha.data_saida,
                    "destino": linha.destino,
                    "retirada": linha.retirada,
                    "linhas": [],
                })
            saidas[indice[chave]]["linhas"].append(linha)
        return saidas

    def _montar_visualizacao(self):
        partes = [
            f"<h2 style='color:{AZUL};margin-bottom:2px;'>"
            "RELATÓRIO DE MÃO DE OBRA</h2>",
        ]
        if self._periodo:
            partes.append(f"<p style='color:{CINZA};'>{self._periodo}</p>")
        if not self._relatorio.tem_dados:
            partes.append("<p>Nenhuma mão de obra no período.</p>")

        # detalhe saída a saída (pulado no modo somente resumo)
        if not self._relatorio.somente_resumo:
            for saida in self._saidas_agrupadas():
                partes.append(self._html_saida(saida))

        # resumo por mão de obra
        partes.append(self._html_resumo())
        self.ui.txt_Visualizacao.setHtml("".join(partes))

    @staticmethod
    def _html_saida(saida: dict) -> str:
        total_saida = sum(linha.total for linha in saida["linhas"])
        titulo = (f"<b>Saída Nº {saida['sequencia']}</b> · "
                  f"{_data_br(saida['data_saida'])}")
        if saida.get("destino"):
            titulo += f" · Destino: {saida['destino']}"
        if saida.get("retirada"):
            titulo += f" · Retirada: {saida['retirada']}"
        html = [
            "<table width='100%' cellspacing='0' cellpadding='0'>"
            f"<tr><td style='background-color:{AZUL};color:#FFFFFF;"
            "padding:6px 8px;font-size:10pt;'>"
            f"{titulo}</td></tr></table>",
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};'>",
            f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
            "<th align='left'>Código</th><th align='left'>Mão de Obra</th>"
            "<th align='right'>Qtde</th><th align='right'>Custo</th>"
            "<th align='right'>Total</th></tr>",
        ]
        for indice, linha in enumerate(saida["linhas"]):
            fundo = ZEBRA if indice % 2 else "#FFFFFF"
            html.append(
                f"<tr style='background-color:{fundo};'>"
                f"<td>{linha.codigo}</td>"
                f"<td>{linha.descricao}</td>"
                f"<td align='right'>{_numero(linha.quantidade)}</td>"
                f"<td align='right'>{_moeda(linha.custo)}</td>"
                f"<td align='right'>{_moeda(linha.total)}</td>"
                "</tr>"
            )
        html.append(
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='4'>Total da Saída</td>"
            f"<td align='right'>{_moeda(total_saida)}</td></tr>"
            "</table><br>"
        )
        return "".join(html)

    def _html_resumo(self) -> str:
        html = [
            "<table width='100%' cellspacing='0' cellpadding='0'>"
            f"<tr><td style='background-color:{AZUL};color:#FFFFFF;"
            "padding:6px 8px;font-size:10pt;'>"
            "<b>RESUMO POR MÃO DE OBRA</b></td></tr></table>",
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};'>",
            f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
            "<th align='left'>Código</th><th align='left'>Mão de Obra</th>"
            "<th align='right'>Qtde</th><th align='right'>Custo</th>"
            "<th align='right'>Total</th></tr>",
        ]
        for indice, linha in enumerate(self._relatorio.resumo):
            fundo = ZEBRA if indice % 2 else "#FFFFFF"
            html.append(
                f"<tr style='background-color:{fundo};'>"
                f"<td>{linha.codigo}</td>"
                f"<td>{linha.descricao}</td>"
                f"<td align='right'>{_numero(linha.quantidade)}</td>"
                f"<td align='right'>{_moeda(linha.custo)}</td>"
                f"<td align='right'>{_moeda(linha.total)}</td>"
                "</tr>"
            )
        html.append(
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='4'>Total geral</td>"
            f"<td align='right'>{_moeda(self._relatorio.total_geral)}</td></tr>"
            "</table>"
        )
        return "".join(html)

    # ---------------- exportação ----------------

    def _gerar_pdf(self):
        from app.reports.relatorio_mao_obra_pdf import gerar_pdf_mao_obra
        self._exportar("PDF (*.pdf)", gerar_pdf_mao_obra)

    def _gerar_xlsx(self):
        from app.reports.relatorio_mao_obra_export import gerar_xlsx_mao_obra
        self._exportar("Excel (*.xlsx)", gerar_xlsx_mao_obra)

    def _gerar_csv(self):
        from app.reports.relatorio_mao_obra_export import gerar_csv_mao_obra
        self._exportar("CSV (*.csv)", gerar_csv_mao_obra)

    def _exportar(self, filtro_arquivo, funcao):
        sugerido = f"Relatorio_Mao_Obra_{datetime.now():%Y-%m-%d}"
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
