# -*- coding: utf-8 -*-
"""Repositório de entradas: acesso a dados (PostgreSQL)."""
from datetime import date

from app.database import get_connection
from app.models.entrada import Entrada, ItemEntrada
from app.utils.logger import get_logger

logger = get_logger("entrada_repository")

_COLUNAS = "motivo_id, motivo_codigo, data_entrada"
_COLUNAS_ITEM = "entrada_id, produto_id, codigo_produto, quantidade, custo"


class EntradaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, entrada: Entrada) -> Entrada:
        """Grava cabeçalho + itens em transação única. Retorna com id."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO entradas ({_COLUNAS}) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (entrada.motivo_id, entrada.motivo_codigo,
                     date.fromisoformat(entrada.data_entrada)),
                )
                entrada.id = cur.fetchone()[0]
                self._inserir_itens(cur, entrada)
        logger.info("Entrada inserida: id=%s (%s itens)",
                    entrada.id, len(entrada.itens))
        return entrada

    def atualizar(self, entrada: Entrada) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "UPDATE entradas SET motivo_id = %s, motivo_codigo = %s, "
                    "data_entrada = %s WHERE id = %s",
                    (entrada.motivo_id, entrada.motivo_codigo,
                     date.fromisoformat(entrada.data_entrada), entrada.id),
                )
                cur.execute(
                    "DELETE FROM itens_entrada WHERE entrada_id = %s",
                    (entrada.id,),
                )
                self._inserir_itens(cur, entrada)
        logger.info("Entrada atualizada: id=%s", entrada.id)
        return True

    def excluir(self, entrada_id: int) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM itens_entrada WHERE entrada_id = %s",
                    (entrada_id,),
                )
                cur.execute(
                    "DELETE FROM entradas WHERE id = %s", (entrada_id,))
        logger.info("Entrada excluída: id=%s", entrada_id)
        return True

    @staticmethod
    def _inserir_itens(cur, entrada: Entrada):
        for item in entrada.itens:
            cur.execute(
                f"INSERT INTO itens_entrada ({_COLUNAS_ITEM}) "
                "VALUES (%s, %s, %s, %s, %s)",
                (entrada.id, item.produto_id, item.codigo_produto,
                 item.quantidade, item.custo),
            )

    # ---------------- leitura ----------------

    def buscar_por_id(self, entrada_id: int) -> Entrada | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, {_COLUNAS} FROM entradas WHERE id = %s",
                    (entrada_id,),
                )
                linha = cur.fetchone()
                if not linha:
                    return None
                entrada = self._linha_para_entrada(linha)
                entrada.itens = self._buscar_itens(cur, entrada.id)
        return entrada

    def pesquisar(self, filtro: str = "") -> list[Entrada]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, {_COLUNAS},
                           (SELECT COALESCE(SUM(quantidade * custo), 0)
                              FROM itens_entrada
                             WHERE entrada_id = entradas.id) AS total
                      FROM entradas
                     WHERE CAST(id AS TEXT) ILIKE %s
                        OR motivo_codigo ILIKE %s
                     ORDER BY id DESC
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [e for e in (self._linha_para_entrada(l) for l in linhas) if e]

    @staticmethod
    def _buscar_itens(cur, entrada_id: int) -> list[ItemEntrada]:
        cur.execute(
            f"SELECT id, {_COLUNAS_ITEM} FROM itens_entrada "
            "WHERE entrada_id = %s ORDER BY id",
            (entrada_id,),
        )
        return [
            ItemEntrada(
                id=l[0], entrada_id=l[1], produto_id=l[2],
                codigo_produto=l[3], quantidade=float(l[4]),
                custo=float(l[5]),
            )
            for l in cur.fetchall()
        ]

    @staticmethod
    def _linha_para_entrada(linha) -> Entrada | None:
        if not linha:
            return None
        data = linha[3]
        return Entrada(
            id=linha[0],
            motivo_id=linha[1],
            motivo_codigo=linha[2],
            data_entrada=data.isoformat() if isinstance(data, date) else str(data),
        )
