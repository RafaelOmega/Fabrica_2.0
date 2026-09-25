# -*- coding: utf-8 -*-
"""Repositório de motivos de entrada: acesso a dados (PostgreSQL)."""
from app.database import get_connection
from app.models.motivo_entrada import MotivoEntrada
from app.utils.logger import get_logger

logger = get_logger("motivo_entrada_repository")

# Colunas para INSERT/UPDATE (id é auto-gerado; 'producao' sem uso)
_COLUNAS = "codigo, descricao, baixa_producao"


class MotivoEntradaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def inserir(self, motivo: MotivoEntrada) -> MotivoEntrada:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO motivos_entrada ({_COLUNAS}) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (motivo.codigo, motivo.descricao, motivo.baixa_producao),
                )
                motivo.id = cur.fetchone()[0]
        logger.info("Motivo inserido: %s (id=%s)", motivo.codigo, motivo.id)
        return motivo

    def atualizar(self, motivo: MotivoEntrada) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE motivos_entrada
                       SET descricao = %s, baixa_producao = %s
                     WHERE codigo = %s
                    """,
                    (motivo.descricao, motivo.baixa_producao, motivo.codigo),
                )
        logger.info("Motivo atualizado: %s", motivo.codigo)
        return True

    def excluir(self, codigo: str) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM motivos_entrada WHERE codigo = %s", (codigo,))
        logger.info("Motivo excluído: %s", codigo)
        return True

    def buscar_por_codigo(self, codigo: str) -> MotivoEntrada | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, {_COLUNAS} FROM motivos_entrada "
                    "WHERE codigo = %s",
                    (codigo,),
                )
                linha = cur.fetchone()
        return self._linha_para_motivo(linha)

    def pesquisar(self, filtro: str = "") -> list[MotivoEntrada]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, {_COLUNAS} FROM motivos_entrada
                     WHERE codigo ILIKE %s OR descricao ILIKE %s
                     ORDER BY codigo
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [m for m in (self._linha_para_motivo(l) for l in linhas) if m]

    @staticmethod
    def _linha_para_motivo(linha) -> MotivoEntrada | None:
        if not linha:
            return None
        return MotivoEntrada(
            id=linha[0],
            codigo=linha[1], descricao=linha[2], baixa_producao=linha[3],
        )
