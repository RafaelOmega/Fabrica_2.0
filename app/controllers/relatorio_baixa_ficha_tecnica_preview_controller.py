# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de baixa de ficha técnica.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
"""
from datetime import datetime

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

from app.models.relatorio_baixa_ficha_tecnica import (
    RelatorioBaixaFichaTecnica,
)
from app.reports.relatorio_baixa_ficha_tecnica_pdf import (
    _data_br, _moeda, _numero,
)
from app.utils.logger import get_logger
from app.views.ui_relatorio_baixa_ficha_tecnica_preview import (
    Ui_Rel_Baixa_Ficha_Tecnica_Preview,
)

logger = get_logger("relatorio_baixa_ficha_tecnica_preview")

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


class RelBaixaFichaTecnicaPreviewController(QDialog):
    """Pré-visualização da baixa de ficha + exportação (PDF/XLSX/CSV)."""

    def __init__(self, relatorio: RelatorioBaixaFichaTecnica, periodo: str,
                 parent=None):
        super().__init__(parent)
        self._relatorio = relatorio
        self._periodo = periodo

        self.ui = Ui_Rel_Baixa_Ficha_Tecnica_Preview()
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
            "RELATÓRIO DE BAIXA DE FICHA TÉCNICA</h2>",
        ]
        if self._periodo:
            partes.append(f"<p style='color:{CINZA};'>{self._periodo}</p>")
        if not self._relatorio.grupos:
            partes.append("<p>Nenhuma baixa de ficha técnica no período.</p>")

        for grupo in self._relatorio.grupos:
            partes.append(self._html_grupo(grupo))
        partes.append(self._html_total_geral())
        self.ui.txt_Visualizacao.setHtml("".join(partes))

    @staticmethod
    def _html_grupo(grupo) -> str:
        html = [
            "<table width='100%' cellspacing='0' cellpadding='0'>"
            f"<tr><td style='background-color:{AZUL};color:#FFFFFF;"
            "padding:6px 8px;font-size:10pt;'>"
            f"<b>{grupo.codigo} - {grupo.descricao}</b></td></tr></table>",
        ]
        for producao in grupo.producoes:
            html.extend([
                f"<p style='color:{CINZA};margin-top:6px;margin-bottom:3px;'>"
                f"<b>Entrada Nº {producao.sequencia}</b> · "
                f"{_data_br(producao.data_entrada)} · produzido: "
                f"<b>{_numero(producao.quantidade)}</b> sacos</p>",
                "<table width='100%' cellspacing='0' cellpadding='4' "
                f"style='border:1px solid {LINHA};font-size:9pt;"
                f"color:{TEXTO};'>",
                f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
                "<th align='left'>Código</th><th align='left'>Insumo</th>"
                "<th align='right'>Qtde</th><th align='right'>Custo</th>"
                "<th align='right'>Total</th><th align='left'>Origem</th></tr>",
            ])
            if producao.itens:
                for indice, item in enumerate(producao.itens):
                    fundo = ZEBRA if indice % 2 else "#FFFFFF"
                    html.append(
                        f"<tr style='background-color:{fundo};'>"
                        f"<td>{item.codigo}</td><td>{item.descricao}</td>"
                        f"<td align='right'>{_numero(item.quantidade_sacos)}</td>"
                        f"<td align='right'>{_moeda(item.custo)}</td>"
                        f"<td align='right'>{_moeda(item.total)}</td>"
                        f"<td>Ent. Nº {item.origem_sequencia}</td></tr>"
                    )
            else:
                html.append(
                    "<tr><td colspan='6' style='color:#888888;'>"
                    "sem ficha técnica cadastrada</td></tr>")
            html.append(
                "<tr style='background-color:#E8EDF2;font-weight:bold;"
                f"color:{TEXTO};'>"
                "<td colspan='5'>Total de insumos da produção</td>"
                f"<td align='right'>{_moeda(producao.total_insumos)}"
                "</td></tr></table>"
            )
        html.append(
            "<p style='margin:2px 0 8px 0;'>"
            f"<b>Total dos insumos {grupo.codigo}: "
            f"{_moeda(grupo.total_insumos)}</b></p>"
        )
        return "".join(html)

    def _html_total_geral(self) -> str:
        return (
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};'>"
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='5'>Total geral</td>"
            f"<td align='right'>{_moeda(self._relatorio.total_geral)}</td></tr>"
            "</table>"
        )

    # ---------------- exportação ----------------

    def _gerar_pdf(self):
        from app.reports.relatorio_baixa_ficha_tecnica_pdf import (
            gerar_pdf_baixa_ficha_tecnica,
        )
        self._exportar("PDF (*.pdf)", gerar_pdf_baixa_ficha_tecnica)

    def _gerar_xlsx(self):
        from app.reports.relatorio_baixa_ficha_tecnica_export import (
            gerar_xlsx_baixa_ficha_tecnica,
        )
        self._exportar("Excel (*.xlsx)", gerar_xlsx_baixa_ficha_tecnica)

    def _gerar_csv(self):
        from app.reports.relatorio_baixa_ficha_tecnica_export import (
            gerar_csv_baixa_ficha_tecnica,
        )
        self._exportar("CSV (*.csv)", gerar_csv_baixa_ficha_tecnica)

    def _exportar(self, filtro_arquivo, funcao):
        sugerido = f"Relatorio_Baixa_Ficha_Tecnica_{datetime.now():%Y-%m-%d}"
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
