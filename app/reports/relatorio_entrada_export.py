# -*- coding: utf-8 -*-
"""Exportação XLSX e CSV do relatório de entradas."""
from datetime import datetime


def _data_br(data_iso: str) -> str:
    """AAAA-MM-DD -> DD/MM/AAAA."""
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


def gerar_xlsx_entradas(relatorio, caminho: str, periodo: str = "") -> None:
    """Gera o XLSX (uma linha por item lançado)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Entradas"
    ws.append(["Entrada Nº", "Data", "Motivo", "Código", "Produto",
               "Qtde", "Custo", "Total"])
    for celula in ws[1]:
        celula.font = Font(bold=True)

    for entrada in relatorio.linhas:
        if entrada.itens:
            for item in entrada.itens:
                ws.append([
                    entrada.sequencia, _data_br(entrada.data_entrada),
                    entrada.motivo_descricao,
                    item.codigo, item.descricao,
                    item.quantidade, item.custo, item.total,
                ])
        else:
            ws.append([
                entrada.sequencia, _data_br(entrada.data_entrada),
                entrada.motivo_descricao,
                "", "sem itens lançados", "", "", entrada.total,
            ])
        ws.append(["", "", f"Total da Entrada Nº {entrada.sequencia}",
                   "", "", "", "", round(entrada.total, 2)])
    ws.append(["", "", "TOTAL GERAL", "", "", "", "",
               round(relatorio.total_geral, 2)])

    wb.save(caminho)


def gerar_csv_entradas(relatorio, caminho: str, periodo: str = "") -> None:
    """Gera o CSV (detalhe)."""
    import csv

    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Entrada Nº", "Data", "Motivo", "Código", "Produto",
                         "Qtde", "Custo", "Total"])
        for entrada in relatorio.linhas:
            if entrada.itens:
                for item in entrada.itens:
                    writer.writerow([
                        entrada.sequencia, _data_br(entrada.data_entrada),
                        entrada.motivo_descricao,
                        item.codigo, item.descricao,
                        item.quantidade, item.custo, item.total,
                    ])
            else:
                writer.writerow([
                    entrada.sequencia, _data_br(entrada.data_entrada),
                    entrada.motivo_descricao,
                    "", "sem itens lançados", "", "", entrada.total,
                ])
            writer.writerow(["", "", f"Total da Entrada Nº {entrada.sequencia}",
                             "", "", "", "", round(entrada.total, 2)])
        writer.writerow(["", "", "TOTAL GERAL", "", "", "", "",
                         round(relatorio.total_geral, 2)])
