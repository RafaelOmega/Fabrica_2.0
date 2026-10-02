# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de mão de obra."""
from datetime import datetime


def _moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero(valor: float) -> str:
    texto = f"{valor:,.4f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _data_br(data_iso: str) -> str:
    """AAAA-MM-DD -> DD/MM/AAAA."""
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


def gerar_pdf_mao_obra(relatorio, caminho: str, periodo: str = "") -> None:
    """Gera o PDF do relatório de mão de obra (detalhe + resumo)."""
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

    # detalhe saída a saída
    saida_atual = None
    total_saida = 0.0
    for linha in relatorio.linhas:
        if linha.saida_id != saida_atual:
            if saida_atual is not None:
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(50 * mm, y, "Total da Saída")
                pdf.drawRightString(190 * mm, y, _moeda(total_saida))
                y -= 5 * mm
            saida_atual = linha.saida_id
            total_saida = 0.0
            y -= 6 * mm
            if y < 25 * mm:
                pdf.showPage()
                y = altura - 20 * mm
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(20 * mm, y,
                           f"Saída Nº {linha.sequencia} · "
                           f"{_data_br(linha.data_saida)}")
            y -= 5 * mm
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(20 * mm, y, "Código")
            pdf.drawString(50 * mm, y, "Mão de Obra")
            pdf.drawRightString(140 * mm, y, "Qtde")
            pdf.drawRightString(160 * mm, y, "Custo")
            pdf.drawRightString(190 * mm, y, "Total")
            y -= 5 * mm
            pdf.setFont("Helvetica", 9)
        total_saida += linha.total
        pdf.drawString(20 * mm, y, str(linha.codigo))
        pdf.drawString(50 * mm, y, linha.descricao[:40])
        pdf.drawRightString(140 * mm, y, _numero(linha.quantidade))
        pdf.drawRightString(160 * mm, y, _moeda(linha.custo))
        pdf.drawRightString(190 * mm, y, _moeda(linha.total))
        y -= 5 * mm
        if y < 25 * mm:
            pdf.showPage()
            y = altura - 20 * mm
    if saida_atual is not None:
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(50 * mm, y, "Total da Saída")
        pdf.drawRightString(190 * mm, y, _moeda(total_saida))
        y -= 5 * mm

    # resumo por mão de obra
    y -= 8 * mm
    if y < 25 * mm:
        pdf.showPage()
        y = altura - 20 * mm
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20 * mm, y, "RESUMO POR MÃO DE OBRA")
    y -= 5 * mm
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(20 * mm, y, "Código")
    pdf.drawString(50 * mm, y, "Mão de Obra")
    pdf.drawRightString(140 * mm, y, "Qtde")
    pdf.drawRightString(160 * mm, y, "Custo")
    pdf.drawRightString(190 * mm, y, "Total")
    y -= 5 * mm
    pdf.setFont("Helvetica", 9)
    for linha in relatorio.resumo:
        pdf.drawString(20 * mm, y, str(linha.codigo))
        pdf.drawString(50 * mm, y, linha.descricao[:40])
        pdf.drawRightString(140 * mm, y, _numero(linha.quantidade))
        pdf.drawRightString(160 * mm, y, _moeda(linha.custo))
        pdf.drawRightString(190 * mm, y, _moeda(linha.total))
        y -= 5 * mm
        if y < 25 * mm:
            pdf.showPage()
            y = altura - 20 * mm
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(20 * mm, y, "Total geral")
    pdf.drawRightString(190 * mm, y, _moeda(relatorio.total_geral))
    pdf.save()
