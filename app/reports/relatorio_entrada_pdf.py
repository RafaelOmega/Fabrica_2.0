# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de entradas (Platypus).

Layout seguindo o padrão dos demais relatórios:
  - Cabeçalho fixo: título, período e emissão
  - Uma seção por entrada: itens lançados + total da entrada
  - Rodapé fixo: sistema à esquerda, "Página X de Y" à direita
"""
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from reportlab.pdfgen import canvas as pdfcanvas

from app.utils.logger import get_logger

logger = get_logger("relatorio_entrada_pdf")

AZUL = colors.HexColor("#1F3B5B")
ZEBRA = colors.HexColor("#F2F5F8")
LINHA = colors.HexColor("#C9D3DE")
CINZA_TXT = colors.HexColor("#5A6B7B")
TEXTO = colors.HexColor("#222222")

_MARGEM = 1.5 * cm
_LARGURA = A4[0] - 2 * _MARGEM

_ESTILO_BARRA = ParagraphStyle("barra", fontName="Helvetica-Bold",
                               fontSize=10, leading=13,
                               textColor=colors.white)
_ESTILO_CELULA = ParagraphStyle("celula", fontName="Helvetica", fontSize=9,
                                leading=11, textColor=TEXTO)
_ESTILO_TOTAL = ParagraphStyle("total", parent=_ESTILO_CELULA, alignment=2)


def _moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero(valor: float, casas: int = 4) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _data_br(iso: str) -> str:
    """AAAA-MM-DD -> dd/mm/aaaa."""
    try:
        ano, mes, dia = iso.split("-")
        return f"{dia}/{mes}/{ano}"
    except (ValueError, AttributeError):
        return iso


class _CanvasPaginado(pdfcanvas.Canvas):
    """Desenha 'Página X de Y' após conhecer o total de páginas."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estados = []

    def showPage(self):
        self._estados.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._estados)
        for estado in self._estados:
            self.__dict__.update(estado)
            self._rodape(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _rodape(self, total: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(CINZA_TXT)
        self.drawString(_MARGEM, 1.0 * cm, "Fábrica 2.0 — Entradas")
        self.drawRightString(A4[0] - _MARGEM, 1.0 * cm,
                             f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _cabecalho(canvas, periodo: str):
    canvas.saveState()
    y = A4[1] - _MARGEM
    canvas.setFillColor(AZUL)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(_MARGEM, y, "RELATÓRIO DE ENTRADAS")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(CINZA_TXT)
    emissao = f"Emitido em {datetime.now():%d/%m/%Y %H:%M}"
    canvas.drawRightString(A4[0] - _MARGEM, y, emissao)
    if periodo:
        canvas.drawString(_MARGEM, y - 14, periodo)
    canvas.setStrokeColor(AZUL)
    canvas.setLineWidth(1.2)
    canvas.line(_MARGEM, y - 22, A4[0] - _MARGEM, y - 22)
    canvas.restoreState()


def _barra_azul(texto: str) -> Table:
    barra = Table([[Paragraph(texto, _ESTILO_BARRA)]],
                  colWidths=[_LARGURA])
    barra.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return barra


def _tabela_itens(linhas: list[list], total_texto: str,
                  total: float) -> Table:
    dados = [["Código", "Produto", "Qtde", "Custo", "Total"]] + linhas + [
        [Paragraph(f"<b>{total_texto}</b>", _ESTILO_CELULA), "", "", "",
         Paragraph(f"<b>{_moeda(total)}</b>", _ESTILO_TOTAL)],
    ]
    tabela = Table(
        dados,
        colWidths=[2.2 * cm, _LARGURA - 9.8 * cm, 2.4 * cm, 2.6 * cm,
                   2.6 * cm],
        repeatRows=1,
    )
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ZEBRA),
        ("TEXTCOLOR", (0, 0), (-1, 0), AZUL),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, ZEBRA]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, AZUL),
        ("GRID", (0, 0), (-1, -2), 0.4, LINHA),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E8EDF2")),
        ("SPAN", (0, -1), (3, -1)),
        ("ALIGN", (2, 0), (4, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabela


def _secao_entrada(entrada) -> list:
    titulo = (f"<b>ENTRADA Nº {entrada.sequencia}</b> · "
              f"{_data_br(entrada.data_entrada)}")
    if entrada.motivo_descricao:
        titulo += f" · {entrada.motivo_descricao}"
    story = [_barra_azul(titulo), Spacer(1, 0.15 * cm)]

    linhas = []
    for item in entrada.itens:
        linhas.append([
            item.codigo,
            Paragraph(item.descricao, _ESTILO_CELULA),
            _numero(item.quantidade),
            _moeda(item.custo),
            _moeda(item.total),
        ])
    if not linhas:
        linhas.append(["", Paragraph("sem itens lançados", _ESTILO_CELULA),
                       "", "", ""])
    story.append(_tabela_itens(linhas, "Total da Entrada", entrada.total))
    return story


def gerar_pdf_entradas(relatorio, caminho: str, periodo: str = "") -> str:
    """Gera o PDF e devolve o caminho escrito."""
    doc = BaseDocTemplate(
        caminho,
        pagesize=A4,
        leftMargin=_MARGEM, rightMargin=_MARGEM,
        topMargin=_MARGEM + 1.0 * cm,
        bottomMargin=_MARGEM + 0.4 * cm,
        title="Relatório de Entradas",
        author="Fábrica 2.0",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="corpo")
    doc.addPageTemplates([
        PageTemplate(id="pagina", frames=[frame],
                     onPage=lambda c, d: _cabecalho(c, periodo))
    ])

    story: list = []
    if not relatorio.tem_dados:
        story.append(Paragraph("Nenhuma entrada no período.",
                               _ESTILO_CELULA))
    for entrada in relatorio.linhas:
        story.append(KeepTogether(_secao_entrada(entrada)))
        story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(
        f"<b>TOTAL GERAL: {_moeda(relatorio.total_geral)}</b>",
        _ESTILO_TOTAL))

    doc.build(story, canvasmaker=_CanvasPaginado)
    logger.info("PDF gerado: %s", caminho)
    return caminho
