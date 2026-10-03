# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de baixa de ficha técnica (Platypus).

Layout seguindo o padrão dos demais relatórios:
  - Cabeçalho fixo: título, período e emissão
  - Sem filtro: agrupado por entrada (acabados + insumos)
  - Com filtro: agrupado por produto acabado (entradas + insumos)
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
_ESTILO_SUB = ParagraphStyle("sub", parent=_ESTILO_CELULA,
                             textColor=CINZA_TXT)


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


def _tabela_itens(linhas: list[list], total_texto: str,
                  total: float) -> Table:
    dados = [["Código", "Insumo", "Qtde", "Custo", "Total", "Origem"]] + \
        linhas + [
            ["", "", "", "",
             Paragraph(f"<b>{total_texto}</b>", _ESTILO_TOTAL),
             Paragraph(f"<b>{_moeda(total)}</b>", _ESTILO_TOTAL)],
    ]
    tabela = Table(
        dados,
        colWidths=[1.9 * cm, _LARGURA - 14.3 * cm, 2.3 * cm, 2.5 * cm,
                   2.5 * cm, 2.4 * cm],
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


def _linhas_de(producao) -> list[list]:
    linhas = []
    for item in producao.itens:
        linhas.append([
            item.codigo,
            Paragraph(item.descricao, _ESTILO_CELULA),
            _numero(item.quantidade_sacos),
            _moeda(item.custo),
            _moeda(item.total),
            f"Ent. Nº {item.origem_sequencia}",
        ])
    if not linhas:
        linhas.append(["", Paragraph("sem ficha técnica", _ESTILO_CELULA),
                       "", "", "", ""])
    return linhas


def _secao_entrada(entrada) -> list:
    titulo = (f"<b>ENTRADA Nº {entrada.sequencia}</b> · "
              f"{_data_br(entrada.data_entrada)}")
    if entrada.motivo_descricao:
        titulo += f" · {entrada.motivo_descricao}"
    story = [_barra_azul(titulo)]
    for ac in entrada.acabados:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"<b>{ac.codigo} - {ac.descricao}</b> · produzido: "
            f"<b>{_numero(ac.quantidade)}</b> sacos", _ESTILO_SUB))
        story.append(Spacer(1, 0.1 * cm))
        story.append(_tabela_itens(
            _linhas_de(ac), f"Total de insumos {ac.codigo}",
            ac.total_insumos))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        f"<b>TOTAL DA ENTRADA Nº {entrada.sequencia}: "
        f"{_moeda(entrada.total)}</b>", _ESTILO_TOTAL))
    return story


def _secao_grupo(grupo) -> list:
    story = [_barra_azul(f"<b>{grupo.codigo} - {grupo.descricao}</b>")]
    for producao in grupo.producoes:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"<b>Entrada Nº {producao.sequencia}</b> · "
            f"{_data_br(producao.data_entrada)} · produzido: "
            f"<b>{_numero(producao.quantidade)}</b> sacos", _ESTILO_SUB))
        story.append(Spacer(1, 0.1 * cm))
        story.append(_tabela_itens(_linhas_de(producao),
                                   "Total de insumos da produção",
                                   producao.total_insumos))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        f"<b>TOTAL DOS INSUMOS {grupo.codigo}: "
        f"{_moeda(grupo.total_insumos)}</b>", _ESTILO_TOTAL))
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
    if not relatorio.tem_dados:
        story.append(Paragraph("Nenhuma baixa de ficha técnica no período.",
                               _ESTILO_CELULA))

    if relatorio.ficha_produto_id:
        for grupo in relatorio.grupos:
            story.append(KeepTogether(_secao_grupo(grupo)))
            story.append(Spacer(1, 0.5 * cm))
    else:
        for entrada in relatorio.entradas:
            story.append(KeepTogether(_secao_entrada(entrada)))
            story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(
        f"<b>TOTAL GERAL: {_moeda(relatorio.total_geral)}</b>",
        _ESTILO_TOTAL))

    doc.build(story, canvasmaker=_CanvasPaginado)
    logger.info("PDF gerado: %s", caminho)
    return caminho
