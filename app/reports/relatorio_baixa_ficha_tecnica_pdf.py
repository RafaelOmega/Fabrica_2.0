# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de baixa de ficha técnica (Platypus).

Layout seguindo o padrão dos demais relatórios:
  - Cabeçalho fixo: título, período e emissão
  - Uma seção por entrada de produção: acabado(s) + itens baixados
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

logger = get_logger("relatorio_baixa_ficha_tecnica_pdf")

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
        self.drawString(_MARGEM, 1.0 * cm,
                        "Fábrica 2.0 — Baixa de Ficha Técnica")
        self.drawRightString(A4[0] - _MARGEM, 1.0 * cm,
                             f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _cabecalho(canvas, periodo: str):
    canvas.saveState()
    y = A4[1] - _MARGEM
    canvas.setFillColor(AZUL)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(_MARGEM, y, "RELATÓRIO DE BAIXA DE FICHA TÉCNICA")
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


def _tabela_padrao(titulos: list[str], linhas: list[list],
                   total_texto: str, total_valor: float) -> Table:
    dados = [titulos] + linhas + [
        ["", "", Paragraph(f"<b>{total_texto}</b>", _ESTILO_TOTAL), "",
         Paragraph(f"<b>{_moeda(total_valor)}</b>", _ESTILO_TOTAL)],
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
        ("SPAN", (0, -1), (2, -1)),
        ("ALIGN", (3, 0), (4, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabela


def _secao_entrada(baixa) -> list:
    titulo = (f"<b>Entrada Nº {baixa.sequencia}</b> · "
              f"{_data_br(baixa.data_entrada)}")
    if baixa.motivo_descricao:
        titulo += f" · {baixa.motivo_descricao}"
    story = [_barra_azul(titulo), Spacer(1, 0.15 * cm)]

    if baixa.acabados:
        linhas = []
        for ac in baixa.acabados:
            linhas.append([
                ac.codigo,
                Paragraph(ac.descricao, _ESTILO_CELULA),
                _numero(ac.quantidade),
                _moeda(ac.custo),
                _moeda(ac.total),
            ])
        story.append(_tabela_padrao(
            ["Código", "Acabado", "Qtde", "Custo", "Total"],
            linhas, "Total Acabados",
            sum(ac.total for ac in baixa.acabados)))
        story.append(Spacer(1, 0.2 * cm))

    linhas_itens = []
    for item in baixa.itens:
        linhas_itens.append([
            item.codigo,
            Paragraph(item.descricao, _ESTILO_CELULA),
            _numero(item.quantidade),
            _moeda(item.custo),
            _moeda(item.total),
        ])
    if not linhas_itens:
        linhas_itens.append([
            "", Paragraph("sem itens baixados", _ESTILO_CELULA),
            "", "", ""])
    story.append(_tabela_padrao(
        ["Código", "Insumo", "Qtde", "Custo", "Total"],
        linhas_itens, "Total da Baixa", baixa.total))
    return story


def gerar_pdf_baixa_ficha_tecnica(relatorio, caminho: str,
                                  periodo: str = "") -> str:
    """Gera o PDF e devolve o caminho escrito."""
    doc = BaseDocTemplate(
        caminho,
        pagesize=A4,
        leftMargin=_MARGEM, rightMargin=_MARGEM,
        topMargin=_MARGEM + 1.0 * cm,
        bottomMargin=_MARGEM + 0.4 * cm,
        title="Relatório de Baixa de Ficha Técnica",
        author="Fábrica 2.0",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="corpo")
    doc.addPageTemplates([
        PageTemplate(id="pagina", frames=[frame],
                     onPage=lambda c, d: _cabecalho(c, periodo))
    ])

    story: list = []
    if not relatorio.linhas:
        story.append(Paragraph("Nenhuma baixa de ficha técnica no período.",
                               _ESTILO_CELULA))
    for baixa in relatorio.linhas:
        story.append(KeepTogether(_secao_entrada(baixa)))
        story.append(Spacer(1, 0.5 * cm))

    # total geral
    story.append(Paragraph(
        f"<b>Total geral: {_moeda(relatorio.total_geral)}</b>",
        _ESTILO_TOTAL))

    doc.build(story, canvasmaker=_CanvasPaginado)
    logger.info("PDF gerado: %s", caminho)
    return caminho
