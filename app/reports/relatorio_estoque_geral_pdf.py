# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de estoque geral (ReportLab / Platypus).

Layout:
  - Cabeçalho fixo: título, período e emissão
  - Tabela única: uma linha por produto (Entradas/Saídas no período,
    Saldo até a data final, Custo Unit. e Valor em Estoque)
  - Linha de total geral
  - Rodapé fixo: sistema à esquerda, "Página X de Y" à direita
"""
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                Paragraph, Table, TableStyle)
from reportlab.pdfgen import canvas as pdfcanvas

from app.models.relatorio_estoque_geral import LinhaEstoqueGeral
from app.utils.logger import get_logger

logger = get_logger("relatorio_estoque_geral_pdf")

AZUL = colors.HexColor("#1F3B5B")
ZEBRA = colors.HexColor("#F2F5F8")
TOTAL = colors.HexColor("#E8EDF2")
CINZA = colors.HexColor("#5A6B7B")

_MARGEM = 1.5 * cm

_ESTILO_CELULA = ParagraphStyle(
    "celula", fontName="Helvetica", fontSize=9, leading=11)
_ESTILO_TOTAL = ParagraphStyle(
    "total", parent=_ESTILO_CELULA, fontName="Helvetica-Bold")


def _data_iso(data: str) -> str:
    """AAAA-MM-DD -> dd/mm/aaaa."""
    return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")


def _numero(valor: float) -> str:
    """1.234,5678 (4 casas, padrão brasileiro)."""
    texto = f"{valor:,.4f}"  # 1,234.5678 (padrão US)
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _moeda(valor: float) -> str:
    """R$ 1.234,56 (2 casas, padrão brasileiro)."""
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class _CanvasPaginado(pdfcanvas.Canvas):
    """Duas passadas para o rodapé "Página X de Y"."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paginas_salvas = []

    def showPage(self):
        self._paginas_salvas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas_salvas)
        for estado in self._paginas_salvas:
            self.__dict__.update(estado)
            self._rodape(total)
            super().showPage()
        super().save()

    def _rodape(self, total: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(CINZA)
        y = 0.75 * cm
        self.drawString(_MARGEM, y, "Fábrica 2.0")
        self.drawRightString(A4[0] - _MARGEM, y,
                             f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _cabecalho(canvas, periodo: str):
    canvas.saveState()
    y = A4[1] - _MARGEM
    canvas.setFillColor(AZUL)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(_MARGEM, y, "RELATÓRIO DE ESTOQUE GERAL")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(CINZA)
    if periodo:
        canvas.drawString(_MARGEM, y - 14, periodo)
    emissao = f"Emitido em {datetime.now():%d/%m/%Y %H:%M}"
    canvas.drawRightString(A4[0] - _MARGEM, y - 14, emissao)
    canvas.line(_MARGEM, y - 22, A4[0] - _MARGEM, y - 22)
    canvas.restoreState()


def _tabela_estoque(linhas: list[LinhaEstoqueGeral]) -> Table:
    dados = [["Produto", "Entradas", "Saídas", "Saldo",
              "Custo Unit.", "Valor em Estoque"]]
    for linha in linhas:
        dados.append([
            Paragraph(f"{linha.codigo} · {linha.descricao}", _ESTILO_CELULA),
            _numero(linha.entradas),
            _numero(linha.saidas),
            _numero(linha.saldo),
            _moeda(linha.custo_unitario),
            _moeda(linha.valor_estoque),
        ])
    dados.append([
        Paragraph("<b>Total geral</b>", _ESTILO_TOTAL),
        Paragraph(f"<b>{_numero(sum(l.entradas for l in linhas))}</b>",
                  _ESTILO_TOTAL),
        Paragraph(f"<b>{_numero(sum(l.saidas for l in linhas))}</b>",
                  _ESTILO_TOTAL),
        Paragraph("—", _ESTILO_TOTAL),
        Paragraph("—", _ESTILO_TOTAL),
        Paragraph(f"<b>{_moeda(sum(l.valor_estoque for l in linhas))}</b>",
                  _ESTILO_TOTAL),
    ])
    tabela = Table(
        dados,
        colWidths=[6.0 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm],
        repeatRows=1,
    )
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DCE4")),
        ("BACKGROUND", (0, -1), (-1, -1), TOTAL),
    ]
    for indice in range(1, len(dados) - 1):
        if indice % 2 == 0:
            estilo.append(("BACKGROUND", (0, indice), (-1, indice), ZEBRA))
    tabela.setStyle(TableStyle(estilo))
    return tabela


def gerar_pdf_estoque_geral(linhas: list[LinhaEstoqueGeral], caminho: str,
                            periodo: str = "") -> str:
    """Gera o PDF e devolve o caminho escrito."""
    doc = BaseDocTemplate(
        caminho,
        pagesize=A4,
        leftMargin=_MARGEM, rightMargin=_MARGEM,
        topMargin=_MARGEM + 1.0 * cm,      # espaço do cabeçalho fixo
        bottomMargin=_MARGEM + 0.4 * cm,   # espaço do rodapé
        title="Relatório de Estoque Geral",
        author="Fábrica 2.0",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="corpo")
    doc.addPageTemplates([
        PageTemplate(
            id="pagina",
            frames=[frame],
            onPage=lambda c, d: _cabecalho(c, periodo),
        )
    ])

    story: list = []
    if not linhas:
        story.append(Paragraph(
            "Nenhum produto com movimentação até a data final.",
            _ESTILO_CELULA))
    else:
        story.append(_tabela_estoque(linhas))
    doc.build(story, canvasmaker=_CanvasPaginado)
    logger.info("PDF gerado: %s", caminho)
    return caminho
