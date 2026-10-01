# -*- coding: utf-8 -*-
"""Repositório de produtos: acesso a dados (PostgreSQL)."""
from app.database import get_connection
from app.models.produto import Produto
from app.utils.logger import get_logger

logger = get_logger("produto_repository")

# Colunas para INSERT/UPDATE (id é auto-gerado pelo banco)
_COLUNAS = (
    "codigo, descricao, unidade, peso, custo, "
    "mat_prima, prod_acabado, mao_obra, controla_estoque, embalagem"
)

# SELECT base com JOIN: traz a descrição da unidade pronta (sem N+1)
_SELECT_BASE = (
    "SELECT p.id, p.codigo, p.descricao, p.unidade, p.peso, p.custo, "
    "p.mat_prima, p.prod_acabado, p.mao_obra, p.controla_estoque, "
    "p.embalagem, um.descricao AS unidade_descricao "
    "FROM produtos p "
    "LEFT JOIN unidades_medida um ON um.codigo = p.unidade"
)


class ProdutoRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def inserir(self, produto: Produto) -> Produto:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO produtos ({_COLUNAS}) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id",
                    (produto.codigo, produto.descricao, produto.unidade,
                     produto.peso, produto.custo, produto.mat_prima,
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
                       SET descricao = %s, unidade = %s, peso = %s, custo = %s,
                           mat_prima = %s, prod_acabado = %s,
                           mao_obra = %s, controla_estoque = %s,
                           embalagem = %s
                     WHERE codigo = %s
                    """,
                    (produto.descricao, produto.unidade, produto.peso,
                     produto.custo, produto.mat_prima, produto.prod_acabado,
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
                    f"{_SELECT_BASE} WHERE p.codigo = %s",
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
                    {_SELECT_BASE}
                     WHERE p.codigo ILIKE %s OR p.descricao ILIKE %s
                     ORDER BY p.codigo
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
            codigo=linha[1], descricao=linha[2], unidade=linha[3] or "",
            unidade_descricao=linha[11] or "",
            peso=linha[4], custo=linha[5], mat_prima=linha[6],
            prod_acabado=linha[7], mao_obra=linha[8],
            controla_estoque=linha[9], embalagem=linha[10],
        )
