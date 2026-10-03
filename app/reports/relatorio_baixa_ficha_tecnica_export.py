# -*- coding: utf-8 -*-
"""Exportação XLSX e CSV do relatório de baixa de ficha técnica."""
from datetime import datetime


def _data_br(data_iso: str) -> str:
    """AAAA-MM-DD -> DD/MM/AAAA."""
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


def _linhas_do_relatorio(relatorio):
    """Gera linhas planas (uma por insumo) agrupadas por entrada."""
    for entrada in relatorio.entradas:
        for ac in entrada.acabados:
            if ac.itens:
                for item in ac.itens:
                    yield [
                        entrada.sequencia, _data_br(entrada.data_entrada),
                        entrada.motivo_descricao,
                        f"{ac.codigo} - {ac.descricao}", ac.quantidade,
                        item.codigo, item.descricao, item.quantidade_sacos,
                        item.custo, item.total,
                        f"Ent. Nº {item.origem_sequencia}",
                    ]
            else:
                yield [
                    entrada.sequencia, _data_br(entrada.data_entrada),
                    entrada.motivo_descricao,
                    f"{ac.codigo} - {ac.descricao}", ac.quantidade,
                    "", "sem ficha técnica", "", "", ac.total_insumos,
                    f"Ent. Nº {entrada.sequencia}",
                ]
        yield ["", "", "", f"Total da Entrada Nº {entrada.sequencia}",
               "", "", "", "", "", round(entrada.total, 2), ""]
        yield None
    yield ["", "", "", "TOTAL GERAL", "", "", "", "", "",
           round(relatorio.total_geral, 2), ""]


def gerar_xlsx_baixa_ficha_tecnica(relatorio, caminho: str,
                                   periodo: str = "") -> None:
    """Gera o XLSX (uma linha por insumo consumido)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Detalhe"
    ws.append(["Entrada Nº", "Data", "Motivo", "Acabado",
               "Qtde Produzida", "Cód Insumo", "Insumo", "Qtde",
               "Custo", "Total", "Origem"])
    for celula in ws[1]:
        celula.font = Font(bold=True)

    for linha in _linhas_do_relatorio(relatorio):
        if linha is None:
            continue
        ws.append(linha)
    wb.save(caminho)


def gerar_csv_baixa_ficha_tecnica(relatorio, caminho: str,
                                  periodo: str = "") -> None:
    """Gera o CSV (detalhe)."""
    import csv

    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Entrada Nº", "Data", "Motivo", "Acabado",
                         "Qtde Produzida", "Cód Insumo", "Insumo", "Qtde",
                         "Custo", "Total", "Origem"])
        for linha in _linhas_do_relatorio(relatorio):
            if linha is None:
                writer.writerow([])
                continue
            writer.writerow(linha)
