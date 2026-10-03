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
    """Gera linhas planas para exportação."""
    for grupo in relatorio.grupos:
        for producao in grupo.producoes:
            if producao.itens:
                for item in producao.itens:
                    yield [
                        grupo.codigo, grupo.descricao,
                        producao.sequencia, _data_br(producao.data_entrada),
                        producao.quantidade,
                        item.codigo, item.descricao,
                        item.quantidade_sacos, item.custo, item.total,
                        f"Ent. Nº {item.origem_sequencia}",
                    ]
            else:
                yield [
                    grupo.codigo, grupo.descricao,
                    producao.sequencia, _data_br(producao.data_entrada),
                    producao.quantidade,
                    "", "sem ficha técnica", "", "", producao.total_insumos,
                    f"Ent. Nº {producao.sequencia}",
                ]
                yield None  # separador após produção
            yield None
        yield None


def gerar_xlsx_baixa_ficha_tecnica(relatorio, caminho: str,
                                   periodo: str = "") -> None:
    """Gera o XLSX (uma linha por insumo consumido)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Detalhe"
    ws.append(["Cód Acabado", "Acabado", "Entrada Nº", "Data",
               "Qtde Produzida", "Cód Insumo", "Insumo", "Qtde",
               "Custo", "Total", "Origem"])
    for celula in ws[1]:
        celula.font = Font(bold=True)

    for linha in _linhas_do_relatorio(relatorio):
        if linha is None:
            continue
        ws.append(linha)
    ws.append(["", "", "", "", "", "", "", "", "", "Total geral",
               round(relatorio.total_geral, 2)])
    wb.save(caminho)


def gerar_csv_baixa_ficha_tecnica(relatorio, caminho: str,
                                  periodo: str = "") -> None:
    """Gera o CSV (detalhe)."""
    import csv

    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Cód Acabado", "Acabado", "Entrada Nº", "Data",
                         "Qtde Produzida", "Cód Insumo", "Insumo", "Qtde",
                         "Custo", "Total", "Origem"])
        for linha in _linhas_do_relatorio(relatorio):
            if linha is None:
                writer.writerow([])
                continue
            writer.writerow(linha)
        writer.writerow(["", "", "", "", "", "", "", "", "", "Total geral",
                         round(relatorio.total_geral, 2)])
