# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de fichas técnicas.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
Aberta pelo botão Filtrar da tela de relatório (a tela de filtros não muda).
"""
from datetime import datetime

from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QMessageBox,
                               QPushButton, QTextBrowser, QVBoxLayout)

from app.reports.relatorio_ficha_tecnica_pdf import (_moeda, _moeda4, _numero,
                                                     _numero_limpo,
                                                     _valor_unitario)
from app.utils.logger import get_logger

logger = get_logger("relatorio_ficha_tecnica_preview")

AZUL = "#1F3B5B"
ZEBRA = "#F2F5F8"
LINHA = "#C9D3DE"
CINZA = "#5A6B7B"


class RelFichaTecnicaPreviewController(QDialog):
    """Pré-visualização do relatório + exportação (PDF/XLSX/CSV)."""

    def __init__(self, fichas, periodo: str, parent=None):
        super().__init__(parent)
        self._fichas = fichas
        self._periodo = periodo

        self.setWindowTitle(
            "Pré-visualização — Relatório de Fichas Técnicas")
        self.resize(860, 600)

        self.txt_Visualizacao = QTextBrowser(self)

        self.bt_PDF = QPushButton("Gerar PDF", self)
        self.bt_XLSX = QPushButton("Gerar XLSX", self)
        self.bt_CSV = QPushButton("Gerar CSV", self)
        self.bt_Fechar = QPushButton("Fechar", self)

        botoes = QHBoxLayout()
        botoes.addWidget(self.bt_PDF)
        botoes.addWidget(self.bt_XLSX)
        botoes.addWidget(self.bt_CSV)
        botoes.addStretch()
        botoes.addWidget(self.bt_Fechar)

        layout = QVBoxLayout(self)
        layout.addWidget(self.txt_Visualizacao)
        layout.addLayout(botoes)

        self.bt_PDF.clicked.connect(self._gerar_pdf)
        self.bt_XLSX.clicked.connect(self._gerar_xlsx)
        self.bt_CSV.clicked.connect(self._gerar_csv)
        self.bt_Fechar.clicked.connect(self.accept)

        self._montar_visualizacao()

    # ---------------- visualização (mesmo layout do PDF) ----------------

    def _montar_visualizacao(self):
        partes = [
            f"<h2 style='color:{AZUL};margin-bottom:2px;'>"
            "RELATÓRIO DE FICHAS TÉCNICAS</h2>",
        ]
        if self._periodo:
            partes.append(f"<p style='color:{CINZA};'>{self._periodo}</p>")
        if not self._fichas:
            partes.append("<p>Nenhuma ficha técnica encontrada.</p>")
        for ficha in self._fichas:
            partes.append(self._html_ficha(ficha))
        self.txt_Visualizacao.setHtml("".join(partes))

    @staticmethod
    def _html_ficha(ficha) -> str:
        unitario = _valor_unitario(ficha)
        titulo = (f"<b>Ficha {ficha.id}</b> — {ficha.codigo_produto} · "
                  f"{ficha.descricao_produto}")
        if unitario is not None:
            titulo += f" · {_moeda(unitario)}/saco"

        html = [
            "<table width='100%' cellspacing='0' cellpadding='0'>"
            f"<tr><td style='background-color:{AZUL};color:white;"
            "padding:6px 8px;font-size:10pt;'>" + titulo + "</td></tr></table>",
            f"<p style='color:{CINZA};'>Sacos por batida: "
            f"<b>{_numero_limpo(ficha.sacos_batida)}</b></p>",
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;'>",
            f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
            "<th align='left'>Código</th><th align='left'>Insumos</th>"
            "<th align='right'>Qtde (kg)</th>"
            "<th align='right'>Custo/Saco</th>"
            "<th align='right'>Custo/kg</th></tr>",
        ]
        if ficha.itens:
            for indice, item in enumerate(ficha.itens):
                fundo = ZEBRA if indice % 2 else "#FFFFFF"
                html.append(
                    f"<tr style='background-color:{fundo};'>"
                    f"<td>{item.codigo_produto}</td>"
                    f"<td>{item.descricao}</td>"
                    f"<td align='right'>{_numero(item.quantidade_kg, 4)}</td>"
                    f"<td align='right'>"
                    f"{_moeda(item.custo_saco) if item.custo_saco is not None else '—'}</td>"
                    f"<td align='right'>"
                    f"{_moeda4(item.custo_kg) if item.custo_kg is not None else '—'}</td>"
                    "</tr>")
        else:
            html.append("<tr><td>—</td><td>sem insumos cadastrados</td>"
                        "<td>—</td><td>—</td><td>—</td></tr>")
        html.append(
            "<tr style='background-color:#E8EDF2;font-weight:bold;'>"
            "<td colspan='2'>Custo da batida</td><td></td><td></td>"
            f"<td align='right'>{_moeda(ficha.custo_batida)}</td></tr>"
            "</table><br>")
        return "".join(html)

    # ---------------- exportação ----------------

    def _gerar_pdf(self):
        from app.reports.relatorio_ficha_tecnica_pdf import (
            gerar_pdf_ficha_tecnica,
        )
        self._exportar("PDF (*.pdf)", gerar_pdf_ficha_tecnica)

    def _gerar_xlsx(self):
        from app.reports.relatorio_ficha_tecnica_export import (
            gerar_xlsx_ficha_tecnica,
        )
        self._exportar("Excel (*.xlsx)", gerar_xlsx_ficha_tecnica)

    def _gerar_csv(self):
        from app.reports.relatorio_ficha_tecnica_export import (
            gerar_csv_ficha_tecnica,
        )
        self._exportar("CSV (*.csv)", gerar_csv_ficha_tecnica)

    def _exportar(self, filtro_arquivo, funcao):
        sugerido = f"Relatorio_Fichas_Tecnicas_{datetime.now():%Y-%m-%d}"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", sugerido, filtro_arquivo)
        if not caminho:
            return
        try:
            funcao(self._fichas, caminho, periodo=self._periodo)
        except Exception as exc:
            QMessageBox.critical(
                self, "Relatório", f"Erro ao gerar o arquivo:\n{exc}")
            return
        logger.info("Arquivo gerado: %s", caminho)
        QMessageBox.information(
            self, "Relatório", f"Arquivo gerado com sucesso:\n{caminho}")
