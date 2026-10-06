# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de mão de obra (ReportLab / Platypus).

Layout seguindo o padrão dos demais relatórios:
  - Cabeçalho fixo: título, período e emissão
  - Detalhe saída a saída: barra azul com número e data + tabela de itens
  - Resumo por mão de obra ao final
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

logger = get_logger("relatorio_mao_obra_pdf")

# ---- paleta (mesma do relatório de kardex / fichas técnicas) ----
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
                        "Fábrica 2.0 — Relatório de Mão de Obra")
        self.drawRightString(A4[0] - _MARGEM, 1.0 * cm,
                             f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _cabecalho(canvas, periodo: str):
    canvas.saveState()
    y = A4[1] - _MARGEM
    canvas.setFillColor(AZUL)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(_MARGEM, y, "RELATÓRIO DE MÃO DE OBRA")
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


def _agrupar_por_saida(linhas):
    """Agrupa as linhas por saída, preservando a ordem."""
    saidas = []
    indice = {}
    for linha in linhas:
        chave = linha.saida_id
        if chave not in indice:
            indice[chave] = len(saidas)
            saidas.append({
                "sequencia": linha.sequencia,
                "data_saida": linha.data_saida,
                "linhas": [],
            })
        saidas[indice[chave]]["linhas"].append(linha)
    return saidas


def _barra_azul(texto: str) -> Table:
    barra = Table(
        [[Paragraph(texto, _ESTILO_BARRA)]],
        colWidths=[_LARGURA],
    )
    barra.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return barra


def _tabela_mao_obra(dados: list) -> Table:
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


def _secao_saida(saida: dict) -> list:
    titulo = (f"<b>Saída Nº {saida['sequencia']}</b> · "
              f"{_data_br(saida['data_saida'])}")
    if saida.get("destino"):
        titulo += f" · Destino: {saida['destino']}"
    if saida.get("retirada"):
        titulo += f" · Retirada: {saida['retirada']}"
    barra = _barra_azul(titulo)

    dados = [["Código", "Mão de Obra", "Qtde", "Custo", "Total"]]
    for linha in saida["linhas"]:
        dados.append([
            linha.codigo,
            Paragraph(linha.descricao, _ESTILO_CELULA),
            _numero(linha.quantidade),
            _moeda(linha.custo),
            _moeda(linha.total),
        ])
    total_saida = sum(linha.total for linha in saida["linhas"])
    dados.append([
        "", "",
        Paragraph("<b>Total da Saída</b>", _ESTILO_TOTAL),
        "",
        Paragraph(f"<b>{_moeda(total_saida)}</b>", _ESTILO_TOTAL),
    ])

    return [barra, Spacer(1, 0.15 * cm), _tabela_mao_obra(dados)]


def _secao_resumo(resumo, total_geral: float) -> list:
    barra = _barra_azul("<b>RESUMO POR MÃO DE OBRA</b>")

    dados = [["Código", "Mão de Obra", "Qtde", "Custo", "Total"]]
    for linha in resumo:
        dados.append([
            linha.codigo,
            Paragraph(linha.descricao, _ESTILO_CELULA),
            _numero(linha.quantidade),
            _moeda(linha.custo),
            _moeda(linha.total),
        ])
    dados.append([
        "", "",
        Paragraph("<b>Total geral</b>", _ESTILO_TOTAL),
        "",
        Paragraph(f"<b>{_moeda(total_geral)}</b>", _ESTILO_TOTAL),
    ])

    return [barra, Spacer(1, 0.15 * cm), _tabela_mao_obra(dados)]


def gerar_pdf_mao_obra(relatorio, caminho: str, periodo: str = "") -> str:
    """Gera o PDF e devolve o caminho escrito."""
    doc = BaseDocTemplate(
        caminho,
        pagesize=A4,
        leftMargin=_MARGEM, rightMargin=_MARGEM,
        topMargin=_MARGEM + 1.0 * cm,      # espaço do cabeçalho fixo
        bottomMargin=_MARGEM + 0.4 * cm,   # espaço do rodapé
        title="Relatório de Mão de Obra",
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
    if not relatorio.tem_dados:
        story.append(Paragraph("Nenhuma mão de obra no período.",
                               _ESTILO_CELULA))

    # detalhe saída a saída (pulado no modo somente resumo; cada saída
    # vai inteira para a próxima página se não couber na atual)
    if not relatorio.somente_resumo:
        for saida in _agrupar_por_saida(relatorio.linhas):
            story.append(KeepTogether(_secao_saida(saida)))
            story.append(Spacer(1, 0.5 * cm))

    # resumo por mão de obra
    if relatorio.resumo:
        story.append(KeepTogether(_secao_resumo(relatorio.resumo,
                                                relatorio.total_geral)))

    doc.build(story, canvasmaker=_CanvasPaginado)
    logger.info("PDF gerado: %s", caminho)
    return caminho
