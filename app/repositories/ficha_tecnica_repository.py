# -*- coding: utf-8 -*-
"""Repositório de fichas técnicas: acesso a dados (PostgreSQL)."""
from app.database import get_connection
from app.models.ficha_tecnica import FichaTecnica, ItemFichaTecnica
from app.utils.logger import get_logger

logger = get_logger("ficha_tecnica_repository")

_COLUNAS_FICHA = "produto_id, codigo_produto, sacos_batida"
_COLUNAS_ITEM = "ficha_id, produto_id, codigo_produto, quantidade_kg"


class FichaTecnicaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- ficha + itens (transação única) ----------------

    def inserir(self, ficha: FichaTecnica) -> FichaTecnica:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO fichas_tecnicas ({_COLUNAS_FICHA}) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (ficha.produto_id, ficha.codigo_produto,
                     ficha.sacos_batida),
                )
                ficha.id = cur.fetchone()[0]
                for item in ficha.itens:
                    cur.execute(
                        f"INSERT INTO itens_ficha_tecnica ({_COLUNAS_ITEM}) "
                        "VALUES (%s, %s, %s, %s)",
                        (ficha.id, item.produto_id, item.codigo_produto,
                         item.quantidade_kg),
                    )
        logger.info("Ficha inserida: id=%s (%s itens)",
                    ficha.id, len(ficha.itens))
        return ficha

    def atualizar(self, ficha: FichaTecnica) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE fichas_tecnicas
                       SET produto_id = %s, codigo_produto = %s,
                           sacos_batida = %s
                     WHERE id = %s
                    """,
                    (ficha.produto_id, ficha.codigo_produto,
                     ficha.sacos_batida, ficha.id),
                )
                # itens: regrava a lista completa
                cur.execute(
                    "DELETE FROM itens_ficha_tecnica WHERE ficha_id = %s",
                    (ficha.id,),
                )
                for item in ficha.itens:
                    cur.execute(
                        f"INSERT INTO itens_ficha_tecnica ({_COLUNAS_ITEM}) "
                        "VALUES (%s, %s, %s, %s)",
                        (ficha.id, item.produto_id, item.codigo_produto,
                         item.quantidade_kg),
                    )
        logger.info("Ficha atualizada: id=%s", ficha.id)
        return True

    def excluir(self, ficha_id: int) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM itens_ficha_tecnica WHERE ficha_id = %s",
                    (ficha_id,),
                )
                cur.execute(
                    "DELETE FROM fichas_tecnicas WHERE id = %s", (ficha_id,))
        logger.info("Ficha excluída: id=%s", ficha_id)
        return True

    # ---------------- consultas ----------------

    def buscar_por_id(self, ficha_id: int) -> FichaTecnica | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, {_COLUNAS_FICHA} "
                    "FROM fichas_tecnicas WHERE id = %s",
                    (ficha_id,),
                )
                linha = cur.fetchone()
                if not linha:
                    return None
                ficha = self._linha_para_ficha(linha)
                ficha.itens = self._buscar_itens(cur, ficha.id)
        return ficha

    def pesquisar(self, filtro: str = "") -> list[FichaTecnica]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT f.id, {_COLUNAS_FICHA}
                      FROM fichas_tecnicas f
                     WHERE f.codigo_produto ILIKE %s
                        OR CAST(f.id AS TEXT) ILIKE %s
                     ORDER BY f.id
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [f for f in (self._linha_para_ficha(l) for l in linhas) if f]

    # ---------------- auxiliares ----------------

    @staticmethod
    def _buscar_itens(cur, ficha_id: int) -> list[ItemFichaTecnica]:
        cur.execute(
            f"SELECT id, {_COLUNAS_ITEM} "
            "FROM itens_ficha_tecnica WHERE ficha_id = %s ORDER BY id",
            (ficha_id,),
        )
        return [
            ItemFichaTecnica(
                id=l[0], ficha_id=l[1], produto_id=l[2],
                codigo_produto=l[3], quantidade_kg=l[4],
            )
            for l in cur.fetchall()
        ]

    @staticmethod
    def _linha_para_ficha(linha) -> FichaTecnica:
        return FichaTecnica(
            id=linha[0],
            produto_id=linha[1],
            codigo_produto=linha[2],
            sacos_batida=linha[3],
        )
