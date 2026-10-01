# -*- coding: utf-8 -*-
"""Geração do relatório de mão de obra (PDF/XLSX/CSV)."""
from datetime import datetime


def _moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero(valor: float) -> str:
    texto = f"{valor:,.4f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_pdf_mao_obra(relatorio, caminho: str, periodo: str = "") -> None:
    """Gera o PDF do relatório de mão de obra."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    pdf = canvas.Canvas(caminho, pagesize=A4)
    largura, altura = A4
    y = altura - 20 * mm
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(20 * mm, y, "RELATÓRIO DE MÃO DE OBRA")
    y -= 8 * mm
    pdf.setFont("Helvetica", 10)
    if periodo:
        pdf.drawString(20 * mm, y, periodo)
        y -= 6 * mm
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(20 * mm, y, "Código")
    pdf.drawString(50 * mm, y, "Mão de Obra")
    pdf.drawRightString(140 * mm, y, "Qtde")
    pdf.drawRightString(160 * mm, y, "Custo")
    pdf.drawRightString(190 * mm, y, "Total")
    y -= 5 * mm
    pdf.setFont("Helvetica", 9)
    for linha in relatorio.linhas:
        pdf.drawString(20 * mm, y, str(linha.codigo))
        pdf.drawString(50 * mm, y, linha.descricao[:40])
        pdf.drawRightString(140 * mm, y, _numero(linha.quantidade))
        pdf.drawRightString(160 * mm, y, _moeda(linha.custo))
        pdf.drawRightString(190 * mm, y, _moeda(linha.total))
        y -= 5 * mm
        if y < 20 * mm:
            pdf.showPage()
            y = altura - 20 * mm
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(20 * mm, y, "Total geral")
    pdf.drawRightString(190 * mm, y, _moeda(relatorio.total_geral))
    pdf.save()


def gerar_xlsx_mao_obra(relatorio, caminho: str, periodo: str = "") -> None:
    """Gera o XLSX do relatório de mão de obra."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Mão de Obra"
    ws.append(["Código", "Mão de Obra", "Qtde", "Custo", "Total"])
    for celula in ws[1]:
        celula.font = Font(bold=True)
    for linha in relatorio.linhas:
        ws.append([
            linha.codigo, linha.descricao,
            linha.quantidade, linha.custo, linha.total,
        ])
    ws.append(["", "", "", "Total geral", relatorio.total_geral])
    wb.save(caminho)


def gerar_csv_mao_obra(relatorio, caminho: str, periodo: str = "") -> None:
    """Gera o CSV do relatório de mão de obra."""
    import csv

    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Código", "Mão de Obra", "Qtde", "Custo", "Total"])
        for linha in relatorio.linhas:
            writer.writerow([
                linha.codigo, linha.descricao,
                linha.quantidade, linha.custo, linha.total,
            ])
        writer.writerow(["", "", "", "Total geral", relatorio.total_geral])
