# -*- coding: utf-8 -*-
"""Exportação do relatório de fichas técnicas para XLSX e CSV.

Mesmos dados e mesma ordem do PDF. XLSX grava valores numéricos com
formato de célula; CSV grava valores já formatados no padrão brasileiro
(separador ';' e BOM para o Excel).
"""
import csv
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from app.models.relatorio_ficha_tecnica import FichaTecnicaRelatorio
from app.reports.relatorio_ficha_tecnica_pdf import (_moeda, _numero_limpo,
                                                     _proporcao,
                                                     _valor_unitario)
from app.utils.logger import get_logger

logger = get_logger("relatorio_ficha_tecnica_export")

AZUL = "1F3B5B"
ZEBRA = "F2F5F8"
TOTAL = "E8EDF2"

_CABECALHOS = ["Cod", "Produto", "Peso", "Custo", "Custo KG",
               "Batida", "Custo Batida", "Qtde Unit.", "Custo Unit."]
_FMT_MOEDA = '"R$" #,##0.00'
_FMT_PESO = "0.####"
_FMT_PROP = "0.##########"


# ---------------- XLSX ----------------

def gerar_xlsx_ficha_tecnica(fichas: list[FichaTecnicaRelatorio],
                             caminho: str, periodo: str = "") -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Fichas Técnicas"

    ws["A1"] = "RELATÓRIO DE FICHAS TÉCNICAS"
    ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    linha = 2
    if periodo:
        ws.cell(linha, 1, periodo)
        linha += 1
    ws.cell(linha, 1, f"Emitido em {datetime.now():%d/%m/%Y %H:%M}")
    linha += 2

    for ficha in fichas:
        linha = _bloco_xlsx(ws, linha, ficha)

    for coluna, largura in zip("ABCDEFGHI",
                               (10, 38, 8, 12, 12, 10, 14, 14, 12)):
        ws.column_dimensions[coluna].width = largura

    wb.save(caminho)
    logger.info("XLSX gerado: %s", caminho)
    return caminho


def _bloco_xlsx(ws, linha: int,
                ficha: FichaTecnicaRelatorio) -> int:
    unitario = _valor_unitario(ficha)
    titulo = (f"Ficha {ficha.id} — {ficha.codigo_produto} · "
              f"{ficha.descricao_produto}")
    if unitario is not None:
        titulo += f" · {_moeda(unitario)}/saco"

    celula = ws.cell(linha, 1, titulo)
    celula.font = Font(bold=True, color="FFFFFF")
    celula.fill = PatternFill("solid", fgColor=AZUL)
    ws.merge_cells(start_row=linha, start_column=1,
                   end_row=linha, end_column=9)
    linha += 1

    ws.cell(linha, 1,
            f"Sacos por batida: {_numero_limpo(ficha.sacos_batida)}")
    linha += 1

    for coluna, texto in enumerate(_CABECALHOS, start=1):
        cel = ws.cell(linha, coluna, texto)
        cel.font = Font(bold=True, color=AZUL)
        cel.fill = PatternFill("solid", fgColor=ZEBRA)
    linha += 1

    if not ficha.itens:
        ws.cell(linha, 1, "—")
        ws.cell(linha, 2, "sem insumos cadastrados")
        linha += 1
    for item in ficha.itens:
        ws.cell(linha, 1, item.codigo_produto)
        ws.cell(linha, 2, item.descricao)
        ws.cell(linha, 3, item.peso_saco).number_format = _FMT_PESO
        if item.custo_saco is not None:
            ws.cell(linha, 4, item.custo_saco).number_format = _FMT_MOEDA
        if item.custo_kg is not None:
            ws.cell(linha, 5, item.custo_kg).number_format = _FMT_MOEDA
        ws.cell(linha, 6, item.quantidade_kg).number_format = _FMT_PESO
        if item.custo_batida is not None:
            ws.cell(linha, 7, item.custo_batida).number_format = _FMT_MOEDA
        qtde_unit = ficha.qtde_unitaria(item)
        if qtde_unit is not None:
            ws.cell(linha, 8, qtde_unit).number_format = _FMT_PROP
        custo_unit = ficha.custo_unitario(item)
        if custo_unit is not None:
            ws.cell(linha, 9, custo_unit).number_format = _FMT_MOEDA
        linha += 1

    total_kg = ficha.total_batida_kg
    cel_rotulo = ws.cell(linha, 2, "Totais")
    cel_rotulo.font = Font(bold=True)
    cel_rotulo.fill = PatternFill("solid", fgColor=TOTAL)
    if total_kg is not None:
        cel_kg = ws.cell(linha, 6, total_kg)
        cel_kg.font = Font(bold=True)
        cel_kg.fill = PatternFill("solid", fgColor=TOTAL)
        cel_kg.number_format = _FMT_PESO
    cel_batida = ws.cell(linha, 7, ficha.custo_batida)
    cel_batida.font = Font(bold=True)
    cel_batida.fill = PatternFill("solid", fgColor=TOTAL)
    cel_batida.number_format = _FMT_MOEDA
    if ficha.peso_produto > 0:
        cel_peso = ws.cell(linha, 8, ficha.peso_produto)
        cel_peso.font = Font(bold=True)
        cel_peso.fill = PatternFill("solid", fgColor=TOTAL)
        cel_peso.number_format = _FMT_PESO
    if unitario is not None:
        cel_unit = ws.cell(linha, 9, unitario)
        cel_unit.font = Font(bold=True)
        cel_unit.fill = PatternFill("solid", fgColor=TOTAL)
        cel_unit.number_format = _FMT_MOEDA
    return linha + 2


# ---------------- CSV ----------------

def gerar_csv_ficha_tecnica(fichas: list[FichaTecnicaRelatorio],
                            caminho: str, periodo: str = "") -> str:
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter=";")
        writer.writerow(["RELATÓRIO DE FICHAS TÉCNICAS"])
        if periodo:
            writer.writerow([periodo])
        writer.writerow([f"Emitido em {datetime.now():%d/%m/%Y %H:%M}"])
        for ficha in fichas:
            writer.writerow([])
            unitario = _valor_unitario(ficha)
            titulo = (f"Ficha {ficha.id} — {ficha.codigo_produto} · "
                      f"{ficha.descricao_produto}")
            if unitario is not None:
                titulo += f" · {_moeda(unitario)}/saco"
            writer.writerow([titulo])
            writer.writerow(
                [f"Sacos por batida: {_numero_limpo(ficha.sacos_batida)}"])
            writer.writerow(_CABECALHOS)
            if not ficha.itens:
                writer.writerow(
                    ["—", "sem insumos cadastrados"] + ["—"] * 7)
            for item in ficha.itens:
                qtde_unit = ficha.qtde_unitaria(item)
                custo_unit = ficha.custo_unitario(item)
                writer.writerow([
                    item.codigo_produto,
                    item.descricao,
                    _numero_limpo(item.peso_saco),
                    _moeda(item.custo_saco)
                    if item.custo_saco is not None else "—",
                    _moeda(item.custo_kg)
                    if item.custo_kg is not None else "—",
                    _numero_limpo(item.quantidade_kg),
                    _moeda(item.custo_batida)
                    if item.custo_batida is not None else "—",
                    _proporcao(qtde_unit)
                    if qtde_unit is not None else "—",
                    _moeda(custo_unit)
                    if custo_unit is not None else "—",
                ])
            total_kg = ficha.total_batida_kg
            writer.writerow([
                "", "Totais", "", "", "",
                _numero_limpo(total_kg) if total_kg is not None else "—",
                _moeda(ficha.custo_batida),
                _numero_limpo(ficha.peso_produto)
                if ficha.peso_produto > 0 else "—",
                _moeda(unitario) if unitario is not None else "—",
            ])
    logger.info("CSV gerado: %s", caminho)
    return caminho
