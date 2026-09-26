# -*- coding: utf-8 -*-
"""Repositório do registro de alterações de custo (PostgreSQL)."""
from app.database import get_connection
from app.models.alteracao_custo import AlteracaoCusto
from app.utils.logger import get_logger

logger = get_logger("alteracao_custo_repository")

_COLUNAS = "produto_id, custo_anterior, custo_novo, origem, entrada_id"


class AlteracaoCustoRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def inserir(self, registro: AlteracaoCusto) -> AlteracaoCusto:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO alteracoes_custo ({_COLUNAS}) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (registro.produto_id, registro.custo_anterior,
                     registro.custo_novo, registro.origem,
                     registro.entrada_id),
                )
                registro.id = cur.fetchone()[0]
        logger.info("Alteração de custo registrada: produto_id=%s "
                    "%.4f -> %.4f (origem=%s)",
                    registro.produto_id, registro.custo_anterior,
                    registro.custo_novo, registro.origem)
        return registro

    def pesquisar(self, produto_id: int | None = None) -> list[AlteracaoCusto]:
        sql = (f"SELECT id, {_COLUNAS}, data_alteracao "
               "FROM alteracoes_custo")
        params: list = []
        if produto_id is not None:
            sql += " WHERE produto_id = %s"
            params.append(produto_id)
        sql += " ORDER BY data_alteracao DESC"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                linhas = cur.fetchall()
        return [
            AlteracaoCusto(
                id=l[0], produto_id=l[1], custo_anterior=float(l[2]),
                custo_novo=float(l[3]), origem=l[4], entrada_id=l[5],
            )
            for l in linhas
        ]
