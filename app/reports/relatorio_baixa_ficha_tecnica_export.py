# -*- coding: utf-8 -*-
"""Exportação XLSX e CSV do relatório de baixa de ficha técnica."""
from datetime import datetime


def _data_br(data_iso: str) -> str:
    """AAAA-MM-DD -> DD/MM/AAAA."""
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


def gerar_xlsx_baixa_ficha_tecnica(relatorio, caminho: str,
                                   periodo: str = "") -> None:
    """Gera o XLSX (aba Detalhe: uma linha por item baixado)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Detalhe"
    ws.append(["Sequência", "Data", "Motivo", "Acabado",
               "Código", "Insumo", "Qtde", "Custo", "Total"])
    for celula in ws[1]:
        celula.font = Font(bold=True)

    for baixa in relatorio.linhas:
        primeira = True
        for item in baixa.itens:
            ws.append([
                baixa.sequencia, _data_br(baixa.data_entrada),
                baixa.motivo_descricao,
                baixa.acabado_texto if primeira else "",
                item.codigo, item.descricao,
                item.quantidade, item.custo, item.total,
            ])
            primeira = False
        if not baixa.itens:
            ws.append([
                baixa.sequencia, _data_br(baixa.data_entrada),
                baixa.motivo_descricao,
                baixa.acabado_texto,
                "", "sem itens baixados", "", "", baixa.total,
            ])
        ws.append(["", "", "", "Total da Baixa", "", "", "",
                   "", round(baixa.total, 2)])
    ws.append(["", "", "", "Total geral", "", "", "", "",
               round(relatorio.total_geral, 2)])

    wb.save(caminho)


def gerar_csv_baixa_ficha_tecnica(relatorio, caminho: str,
                                  periodo: str = "") -> None:
    """Gera o CSV do relatório (detalhe)."""
    import csv

    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Sequência", "Data", "Motivo", "Acabado",
                         "Código", "Insumo", "Qtde", "Custo", "Total"])
        for baixa in relatorio.linhas:
            primeira = True
            for item in baixa.itens:
                writer.writerow([
                    baixa.sequencia, _data_br(baixa.data_entrada),
                    baixa.motivo_descricao,
                    baixa.acabado_texto if primeira else "",
                    item.codigo, item.descricao,
                    item.quantidade, item.custo, item.total,
                ])
                primeira = False
            if not baixa.itens:
                writer.writerow([
                    baixa.sequencia, _data_br(baixa.data_entrada),
                    baixa.motivo_descricao,
                    baixa.acabado_texto,
                    "", "sem itens baixados", "", "", baixa.total,
                ])
            writer.writerow(["", "", "", "Total da Baixa", "",
                             "", "", "", round(baixa.total, 2)])
        writer.writerow(["", "", "", "Total geral", "",
                         "", "", "", round(relatorio.total_geral, 2)])
