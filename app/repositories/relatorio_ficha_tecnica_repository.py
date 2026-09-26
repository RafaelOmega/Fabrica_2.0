# -*- coding: utf-8 -*-
"""Repositório do relatório de fichas técnicas (PostgreSQL)."""
from app.database import get_connection
from app.models.relatorio_ficha_tecnica import (
    FichaTecnicaRelatorio, InsumoRelatorio,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_ficha_tecnica_repository")


class RelatorioFichaTecnicaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def fichas_tecnicas(self, filtro: str = "") -> list[FichaTecnicaRelatorio]:
        """Fichas + insumos (descrição, peso e custo do cadastro de produtos).

        Filtro vazio retorna todas as fichas; quando preenchido, busca
        por descrição do produto acabado, código ou ID da ficha.
        """
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT f.id, f.codigo_produto, p.descricao,
                           f.sacos_batida
                      FROM fichas_tecnicas f
                      LEFT JOIN produtos p ON p.id = f.produto_id
                     WHERE (%s = ''
                            OR p.descricao ILIKE %s
                            OR f.codigo_produto ILIKE %s
                            OR CAST(f.id AS TEXT) ILIKE %s)
                     ORDER BY p.descricao, f.id
                    """,
                    (filtro, termo, termo, termo),
                )
                fichas = [
                    FichaTecnicaRelatorio(
                        id=l[0], codigo_produto=l[1],
                        descricao_produto=l[2] or "",
                        sacos_batida=float(l[3]),
                    )
                    for l in cur.fetchall()
                ]
                for ficha in fichas:
                    ficha.itens = self._itens(cur, ficha.id)
        logger.info("Relatório: %s ficha(s) carregada(s)", len(fichas))
        return fichas

    def descricao_da_ficha(self, ficha_id: int) -> str:
        """Descrição do produto acabado da ficha (para o campo de filtro)."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.descricao
                      FROM fichas_tecnicas f
                      LEFT JOIN produtos p ON p.id = f.produto_id
                     WHERE f.id = %s
                    """,
                    (ficha_id,),
                )
                linha = cur.fetchone()
        return linha[0] if linha and linha[0] else ""

    @staticmethod
    def _itens(cur, ficha_id: int) -> list[InsumoRelatorio]:
        cur.execute(
            """
            SELECT i.codigo_produto, p.descricao,
                   i.quantidade_kg, p.custo, p.peso
              FROM itens_ficha_tecnica i
              LEFT JOIN produtos p ON p.id = i.produto_id
             WHERE i.ficha_id = %s
             ORDER BY i.id
            """,
            (ficha_id,),
        )
        return [
            InsumoRelatorio(
                codigo_produto=l[0], descricao=l[1] or "",
                quantidade_kg=float(l[2]),
                custo_saco=float(l[3]) if l[3] is not None else None,
                peso_saco=float(l[4]) if l[4] is not None else 0.0,
            )
            for l in cur.fetchall()
        ]
