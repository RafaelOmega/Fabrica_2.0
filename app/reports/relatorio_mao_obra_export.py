# -*- coding: utf-8 -*-
"""Exportação XLSX e CSV do relatório de mão de obra."""


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
