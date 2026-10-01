# -*- coding: utf-8 -*-
"""Repositório de unidades de medida: acesso a dados (PostgreSQL).

Schema:
  unidades_medida (id, codigo, descricao, fator_conversao)
"""
from app.database import get_connection
from app.models.unidade_medida import UnidadeMedida
from app.utils.logger import get_logger

logger = get_logger("unidade_medida_repository")

_COLUNAS = "codigo, descricao, fator_conversao"


class UnidadeMedidaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, unidade: UnidadeMedida) -> UnidadeMedida:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO unidades_medida ({_COLUNAS}) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (unidade.codigo, unidade.descricao,
                     unidade.fator_conversao),
                )
                unidade.id = cur.fetchone()[0]
        logger.info("Unidade inserida: %s", unidade.codigo)
        return unidade

    def atualizar(self, unidade: UnidadeMedida) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "UPDATE unidades_medida "
                    "SET descricao = %s, fator_conversao = %s "
                    "WHERE codigo = %s",
                    (unidade.descricao, unidade.fator_conversao,
                     unidade.codigo),
                )
                atualizado = cur.rowcount > 0
        logger.info("Unidade atualizada: %s (%s)", unidade.codigo, atualizado)
        return atualizado

    def excluir(self, codigo: str) -> bool:
        """Exclui a unidade, bloqueando se estiver em uso por produtos."""
        with self._conn:
            with self._conn.cursor() as cur:
                # proteção: unidade vinculada a produto não pode ser excluída
                cur.execute(
                    "SELECT 1 FROM produtos WHERE unidade = %s LIMIT 1",
                    (codigo,),
                )
                if cur.fetchone():
                    raise ValueError(
                        "Unidade em uso por produtos — exclusão bloqueada.")
                cur.execute(
                    "DELETE FROM unidades_medida WHERE codigo = %s",
                    (codigo,),
                )
                excluido = cur.rowcount > 0
        logger.info("Unidade excluída: %s (%s)", codigo, excluido)
        return excluido

    # ---------------- leitura ----------------

    def buscar_por_codigo(self, codigo: str) -> UnidadeMedida | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT id, codigo, descricao, fator_conversao "
                    "FROM unidades_medida WHERE codigo = %s",
                    (codigo,),
                )
                linha = cur.fetchone()
        return self._linha_para_unidade(linha)

    def pesquisar(self, filtro: str = "") -> list[UnidadeMedida]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, codigo, descricao, fator_conversao
                      FROM unidades_medida
                     WHERE codigo ILIKE %s
                        OR descricao ILIKE %s
                     ORDER BY codigo
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [u for u in (self._linha_para_unidade(l) for l in linhas) if u]

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_unidade(linha) -> UnidadeMedida | None:
        if not linha:
            return None
        return UnidadeMedida(
            id=linha[0],
            codigo=linha[1] or "",
            descricao=linha[2] or "",
            fator_conversao=float(linha[3] or 0),
        )
