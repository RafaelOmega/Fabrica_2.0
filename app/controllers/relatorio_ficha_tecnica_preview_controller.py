# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de fichas técnicas.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
Aberta pelo botão Filtrar da tela de relatório (a tela de filtros não muda).

O QTextBrowser usa folha de estilo própria (fundo branco, "papel"),
pois o tema escuro global do sistema torna o HTML claro ilegível.
"""
from datetime import datetime

from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QMessageBox,
                               QPushButton, QTextBrowser, QVBoxLayout)

from app.reports.relatorio_ficha_tecnica_pdf import (_moeda, _numero_limpo,
                                                     _proporcao,
                                                     _valor_unitario)
from app.utils.logger import get_logger

logger = get_logger("relatorio_ficha_tecnica_preview")

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


class RelFichaTecnicaPreviewController(QDialog):
    """Pré-visualização do relatório + exportação (PDF/XLSX/CSV)."""

    def __init__(self, fichas, periodo: str, parent=None):
        super().__init__(parent)
        self._fichas = fichas
        self._periodo = periodo

        self.setWindowTitle(
            "Pré-visualização — Relatório de Fichas Técnicas")
        self.resize(980, 600)

        self.txt_Visualizacao = QTextBrowser(self)
        self.txt_Visualizacao.setStyleSheet(_ESTILO_PAPEL)

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
            f"<tr><td style='background-color:{AZUL};color:#FFFFFF;"
            "padding:6px 8px;font-size:10pt;'>" + titulo + "</td></tr></table>",
            f"<p style='color:{CINZA};'>Sacos por batida: "
            f"<b>{_numero_limpo(ficha.sacos_batida)}</b></p>",
            "<table width='100%' cellspacing='0' cellpadding='4' "
            f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};'>",
            f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
            "<th align='left'>Cod</th><th align='left'>Produto</th>"
            "<th align='right'>Peso</th>"
            "<th align='right'>Custo</th>"
            "<th align='right'>Custo KG</th>"
            "<th align='right'>Batida</th>"
            "<th align='right'>Custo Batida</th>"
            "<th align='right'>Qtde Unit.</th>"
            "<th align='right'>Custo Unit.</th></tr>",
        ]
        if ficha.itens:
            for indice, item in enumerate(ficha.itens):
                fundo = ZEBRA if indice % 2 else "#FFFFFF"
                qtde_unit = ficha.qtde_unitaria(item)
                custo_unit = ficha.custo_unitario(item)
                html.append(
                    f"<tr style='background-color:{fundo};'>"
                    f"<td>{item.codigo_produto}</td>"
                    f"<td>{item.descricao}</td>"
                    f"<td align='right'>{_numero_limpo(item.peso_saco)}</td>"
                    f"<td align='right'>"
                    f"{_moeda(item.custo_saco) if item.custo_saco is not None else '—'}</td>"
                    f"<td align='right'>"
                    f"{_moeda(item.custo_kg) if item.custo_kg is not None else '—'}</td>"
                    f"<td align='right'>{_numero_limpo(item.quantidade_kg)}</td>"
                    f"<td align='right'>"
                    f"{_moeda(item.custo_batida) if item.custo_batida is not None else '—'}</td>"
                    f"<td align='right'>"
                    f"{_proporcao(qtde_unit) if qtde_unit is not None else '—'}</td>"
                    f"<td align='right'>"
                    f"{_moeda(custo_unit) if custo_unit is not None else '—'}</td>"
                    "</tr>")
        else:
            html.append("<tr><td>—</td><td>sem insumos cadastrados</td>"
                        "<td>—</td><td>—</td><td>—</td><td>—</td>"
                        "<td>—</td><td>—</td><td>—</td></tr>")

        total_kg = ficha.total_batida_kg
        html.append(
            "<tr style='background-color:#E8EDF2;font-weight:bold;"
            f"color:{TEXTO};'>"
            "<td colspan='2'>Totais</td><td></td><td></td><td></td>"
            f"<td align='right'>"
            f"{_numero_limpo(total_kg) if total_kg is not None else '—'}</td>"
            f"<td align='right'>{_moeda(ficha.custo_batida)}</td>"
            f"<td align='right'>"
            f"{_numero_limpo(ficha.peso_produto) if ficha.peso_produto > 0 else '—'}</td>"
            f"<td align='right'>"
            f"{_moeda(unitario) if unitario is not None else '—'}</td>"
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
