# -*- coding: utf-8 -*-
"""Repositório de produtos: acesso a dados (PostgreSQL)."""
from app.database import get_connection
from app.models.produto import Produto
from app.utils.logger import get_logger

logger = get_logger("produto_repository")

# Colunas para INSERT/UPDATE (id é auto-gerado pelo banco)
_COLUNAS = (
    "codigo, descricao, peso, custo, "
    "mat_prima, prod_acabado, mao_obra, controla_estoque, embalagem"
)


class ProdutoRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def inserir(self, produto: Produto) -> Produto:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO produtos ({_COLUNAS}) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id",
                    (produto.codigo, produto.descricao, produto.peso,
                     produto.custo, produto.mat_prima,
                     produto.prod_acabado, produto.mao_obra,
                     produto.controla_estoque, produto.embalagem),
                )
                produto.id = cur.fetchone()[0]
        logger.info("Produto inserido: %s (id=%s)", produto.codigo, produto.id)
        return produto

    def atualizar(self, produto: Produto) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE produtos
                       SET descricao = %s, peso = %s, custo = %s,
                           mat_prima = %s, prod_acabado = %s,
                           mao_obra = %s, controla_estoque = %s,
                           embalagem = %s
                     WHERE codigo = %s
                    """,
                    (produto.descricao, produto.peso, produto.custo,
                     produto.mat_prima, produto.prod_acabado,
                     produto.mao_obra, produto.controla_estoque,
                     produto.embalagem, produto.codigo),
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
                    f"SELECT id, {_COLUNAS} FROM produtos WHERE codigo = %s",
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
                    SELECT id, {_COLUNAS} FROM produtos
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
            id=linha[0],
            codigo=linha[1], descricao=linha[2], peso=linha[3],
            custo=linha[4], mat_prima=linha[5],
            prod_acabado=linha[6], mao_obra=linha[7],
            controla_estoque=linha[8], embalagem=linha[9],
        )
