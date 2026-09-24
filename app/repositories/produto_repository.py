# -*- coding: utf-8 -*-
"""Repositório de produtos: acesso a dados (PostgreSQL)."""
from app.database import get_connection
from app.models.produto import Produto
from app.utils.logger import get_logger

logger = get_logger("produto_repository")

_COLUNAS = (
    "codigo, descricao, peso, custo, "
    "materia_prima, produto_acabado, mao_obra, controla_estoque"
)


class ProdutoRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def inserir(self, produto: Produto) -> Produto:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO produtos ({_COLUNAS}) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (produto.codigo, produto.descricao, produto.peso,
                     produto.custo, produto.materia_prima,
                     produto.produto_acabado, produto.mao_obra,
                     produto.controla_estoque),
                )
        logger.info("Produto inserido: %s", produto.codigo)
        return produto

    def atualizar(self, produto: Produto) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE produtos
                       SET descricao = %s, peso = %s, custo = %s,
                           materia_prima = %s, produto_acabado = %s,
                           mao_obra = %s, controla_estoque = %s
                     WHERE codigo = %s
                    """,
                    (produto.descricao, produto.peso, produto.custo,
                     produto.materia_prima, produto.produto_acabado,
                     produto.mao_obra, produto.controla_estoque,
                     produto.codigo),
                )
        logger.info("Produto atualizado: %s", produto.codigo)
        return True

    def excluir(self, codigo: str) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM produtos WHERE codigo = %s", (codigo,))
        logger.info("Produto excluído: %s", codigo)
        return True

    def buscar_por_codigo(self, codigo: str) -> Produto | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"SELECT {_COLUNAS} FROM produtos WHERE codigo = %s",
                    (codigo,),
                )
                linha = cur.fetchone()
        return self._linha_para_produto(linha)

    def pesquisar(self, filtro: str = "") -> list[Produto]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {_COLUNAS} FROM produtos
                     WHERE codigo ILIKE %s OR descricao ILIKE %s
                     ORDER BY codigo
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [p for p in (self._linha_para_produto(l) for l in linhas) if p]

    @staticmethod
    def _linha_para_produto(linha) -> Produto | None:
        if not linha:
            return None
        return Produto(
            codigo=linha[0], descricao=linha[1], peso=linha[2],
            custo=linha[3], materia_prima=linha[4],
            produto_acabado=linha[5], mao_obra=linha[6],
            controla_estoque=linha[7],
        )
