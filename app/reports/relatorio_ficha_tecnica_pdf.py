# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de fichas técnicas (ReportLab / Platypus).

Layout:
  - Página A4 PAISAGEM (9 colunas não cabem legíveis em retrato)
  - Cabeçalho fixo: título, período do filtro e emissão
  - Uma seção por ficha: identificação + tabela de insumos + totais
  - Valor unitário do produto acabado junto à descrição (custo_batida / sacos)
  - Ficha nunca quebrada no meio: cada seção entra inteira na página
  - Rodapé fixo: sistema à esquerda, "Página X de Y" à direita

Fontes: Segoe UI (Semibold para títulos/cabeçalhos, regular para células,
Light apenas em texto de apoio). Fallback automático para Helvetica
quando os arquivos .ttf do Windows não existirem.
"""
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from reportlab.pdfgen import canvas as pdfcanvas

from app.models.relatorio_ficha_tecnica import FichaTecnicaRelatorio
from app.utils.logger import get_logger

logger = get_logger("relatorio_ficha_tecnica_pdf")

# ---------------- fontes (Segoe UI com fallback) ----------------

_FONTES_WINDOWS = {
    "Segoe UI": r"C:\Windows\Fonts\segoeui.ttf",
    "Segoe UI Semibold": r"C:\Windows\Fonts\segoeuisb.ttf",
    "Segoe UI Light": r"C:\Windows\Fonts\segoeuil.ttf",
}

try:
    for nome, caminho in _FONTES_WINDOWS.items():
        if os.path.exists(caminho):
            pdfmetrics.registerFont(TTFont(nome, caminho))
except Exception:
    logger.exception("Falha ao registrar fontes Segoe UI")

# nomes efetivos: caem para Helvetica se a Segoe não registrou
_F_TITULO = ("Segoe UI Semibold"
             if "Segoe UI Semibold" in pdfmetrics.getRegisteredFontNames()
             else "Helvetica-Bold")
_F_CORPO = ("Segoe UI"
            if "Segoe UI" in pdfmetrics.getRegisteredFontNames()
            else "Helvetica")
_F_APOIO = ("Segoe UI Light"
            if "Segoe UI Light" in pdfmetrics.getRegisteredFontNames()
            else _F_CORPO)

# ---- paleta ----
AZUL = colors.HexColor("#1F3B5B")
ZEBRA = colors.HexColor("#F2F5F8")
LINHA = colors.HexColor("#C9D3DE")
CINZA_TXT = colors.HexColor("#5A6B7B")
TEXTO = colors.HexColor("#222222")

# ---- página: A4 paisagem ----
PAGINA = landscape(A4)

_MARGEM = 1.5 * cm
_LARGURA = PAGINA[0] - 2 * _MARGEM

_ESTILO_BARRA = ParagraphStyle("barra", fontName=_F_TITULO,
                               fontSize=10, leading=13,
                               textColor=colors.white)
_ESTILO_CELULA = ParagraphStyle("celula", fontName=_F_CORPO, fontSize=9,
                                leading=11, textColor=TEXTO)
_ESTILO_TOTAL = ParagraphStyle("total", parent=_ESTILO_CELULA, alignment=2)


def _moeda(valor: float) -> str:
    """Formata no padrão brasileiro: R$ 1.234,56 (sem locale)."""
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _moeda4(valor: float) -> str:
    """Formata valor monetário com 4 casas: R$ 0,4167 (sem locale)."""
    texto = f"{valor:,.4f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero(valor: float, casas: int = 4) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero_limpo(valor: float) -> str:
    if valor == int(valor):
        return str(int(valor))
    return _numero(valor, 2)


def _proporcao(valor: float) -> str:
    """Proporção por saco como no layout legado: até 10 dígitos
    significativos, vírgula decimal, sem separador de milhar."""
    texto = f"{valor:.10g}"
    return texto.replace(".", ",")


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
        self.setFont(_F_APOIO, 8)
        self.setFillColor(CINZA_TXT)
        self.drawString(_MARGEM, 1.0 * cm,
                        "Fábrica 2.0 — Relatório de Fichas Técnicas")
        self.drawRightString(PAGINA[0] - _MARGEM, 1.0 * cm,
                             f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _cabecalho(canvas, periodo: str):
    canvas.saveState()
    y = PAGINA[1] - _MARGEM
    canvas.setFillColor(AZUL)
    canvas.setFont(_F_TITULO, 14)
    canvas.drawString(_MARGEM, y, "RELATÓRIO DE FICHAS TÉCNICAS")
    canvas.setFont(_F_APOIO, 9)
    canvas.setFillColor(CINZA_TXT)
    emissao = f"Emitido em {datetime.now():%d/%m/%Y %H:%M}"
    canvas.drawRightString(PAGINA[0] - _MARGEM, y, emissao)
    if periodo:
        canvas.drawString(_MARGEM, y - 14, periodo)
    canvas.setStrokeColor(AZUL)
    canvas.setLineWidth(1.2)
    canvas.line(_MARGEM, y - 22, PAGINA[0] - _MARGEM, y - 22)
    canvas.restoreState()


def _valor_unitario(ficha: FichaTecnicaRelatorio) -> float | None:
    """Valor unitário do produto acabado (custo da batida / sacos por batida)."""
    return ficha.custo_unitario_total


def _secao_ficha(ficha: FichaTecnicaRelatorio) -> list:
    # valor unitário junto à descrição do produto acabado (sem coluna nova)
    unitario = _valor_unitario(ficha)
    titulo = (f"<b>Ficha {ficha.id}</b> — {ficha.codigo_produto} · "
              f"{ficha.descricao_produto}")
    if unitario is not None:
        titulo += f" · {_moeda(unitario)}/saco"
    barra = Table([[Paragraph(titulo, _ESTILO_BARRA)]],
                  colWidths=[_LARGURA])
    barra.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    info = Paragraph(
        f"Sacos por batida: <b>{_numero_limpo(ficha.sacos_batida)}</b>",
        ParagraphStyle("info", fontName=_F_APOIO, fontSize=9, leading=11,
                       textColor=CINZA_TXT))

    dados = [["Cod", "Produto", "Peso", "Custo", "Custo KG",
              "Batida", "Custo Batida", "Qtde Unit.", "Custo Unit."]]
    for item in ficha.itens:
        qtde_unit = ficha.qtde_unitaria(item)
        custo_unit = ficha.custo_unitario(item)
        dados.append([
            item.codigo_produto,
            Paragraph(item.descricao, _ESTILO_CELULA),
            _numero_limpo(item.peso_saco),
            # Custo: apenas informativo (custo cadastrado do produto)
            _moeda(item.custo_saco) if item.custo_saco is not None else "—",
            # Custo KG: custo cadastrado / peso do produto
            _moeda(item.custo_kg) if item.custo_kg is not None else "—",
            _numero_limpo(item.quantidade_kg),
            _moeda(item.custo_batida) if item.custo_batida is not None else "—",
            _proporcao(qtde_unit) if qtde_unit is not None else "—",
            _moeda(custo_unit) if custo_unit is not None else "—",
        ])
    if len(dados) == 1:
        dados.append(["—", "sem insumos cadastrados"] + ["—"] * 7)

    total_kg = ficha.total_batida_kg
    dados.append([
        "",
        Paragraph("<b>Totais</b>", _ESTILO_TOTAL),
        "",
        "",
        "",
        Paragraph(f"<b>{_numero_limpo(total_kg)}</b>"
                  if total_kg is not None else "—", _ESTILO_TOTAL),
        Paragraph(f"<b>{_moeda(ficha.custo_batida)}</b>", _ESTILO_TOTAL),
        Paragraph(f"<b>{_numero_limpo(ficha.peso_produto)}</b>"
                  if ficha.peso_produto > 0 else "—", _ESTILO_TOTAL),
        Paragraph(f"<b>{_moeda(unitario)}</b>"
                  if unitario is not None else "—", _ESTILO_TOTAL),
    ])

    tabela = Table(
        dados,
        colWidths=[2.0 * cm, _LARGURA - 17.8 * cm, 1.8 * cm, 2.2 * cm,
                   2.2 * cm, 2.2 * cm, 2.6 * cm, 2.6 * cm, 2.2 * cm],
        repeatRows=1,
    )
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ZEBRA),
        ("TEXTCOLOR", (0, 0), (-1, 0), AZUL),
        ("FONTNAME", (0, 0), (-1, 0), _F_TITULO),
        ("FONTNAME", (0, 1), (-1, -2), _F_CORPO),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, ZEBRA]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, AZUL),
        ("GRID", (0, 0), (-1, -2), 0.4, LINHA),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E8EDF2")),
        ("SPAN", (0, -1), (1, -1)),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    return [barra, Spacer(1, 0.15 * cm), info,
            Spacer(1, 0.15 * cm), tabela]


def gerar_pdf_ficha_tecnica(fichas: list[FichaTecnicaRelatorio],
                            caminho: str, periodo: str = "") -> str:
    """Gera o PDF e devolve o caminho escrito."""
    doc = BaseDocTemplate(
        caminho,
        pagesize=PAGINA,
        leftMargin=_MARGEM, rightMargin=_MARGEM,
        topMargin=_MARGEM + 1.0 * cm,      # espaço do cabeçalho fixo
        bottomMargin=_MARGEM + 0.4 * cm,   # espaço do rodapé
        title="Relatório de Fichas Técnicas",
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
    if not fichas:
        story.append(Paragraph("Nenhuma ficha técnica encontrada.",
                               _ESTILO_CELULA))
    for indice, ficha in enumerate(fichas):
        if indice:
            story.append(Spacer(1, 0.7 * cm))
        # KeepTogether: a ficha vai inteira para a próxima página se
        # não couber na atual (só quebra se for maior que a página).
        story.append(KeepTogether(_secao_ficha(ficha)))

    doc.build(story, canvasmaker=_CanvasPaginado)
    logger.info("PDF gerado: %s", caminho)
    return caminho
