# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: cada comando usa
CREATE TABLE/INDEX IF NOT EXISTS, portanto em bancos já existentes
nada é alterado; em banco novo, todas as tabelas são criadas.
"""
from app.database.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("schema")

_COMANDOS = (
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id               SERIAL PRIMARY KEY,
        codigo           VARCHAR(20) NOT NULL UNIQUE,
        descricao        VARCHAR(120) NOT NULL,
        peso             NUMERIC(12,4) NOT NULL DEFAULT 0,
        custo            NUMERIC(12,4) NOT NULL DEFAULT 0,
        mat_prima        BOOLEAN NOT NULL DEFAULT FALSE,
        prod_acabado     BOOLEAN NOT NULL DEFAULT FALSE,
        mao_obra         BOOLEAN NOT NULL DEFAULT FALSE,
        controla_estoque BOOLEAN NOT NULL DEFAULT FALSE,
        embalagem        BOOLEAN NOT NULL DEFAULT FALSE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS motivos_entrada (
        id             SERIAL PRIMARY KEY,
        codigo         VARCHAR(20) NOT NULL UNIQUE,
        descricao      VARCHAR(120) NOT NULL,
        baixa_producao BOOLEAN NOT NULL DEFAULT FALSE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fichas_tecnicas (
        id             SERIAL PRIMARY KEY,
        produto_id     INTEGER REFERENCES produtos(id),
        codigo_produto VARCHAR(20) NOT NULL,
        sacos_batida   NUMERIC(12,4) NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_ficha_tecnica (
        id             SERIAL PRIMARY KEY,
        ficha_id       INTEGER NOT NULL
                       REFERENCES fichas_tecnicas(id) ON DELETE CASCADE,
        produto_id     INTEGER REFERENCES produtos(id),
        codigo_produto VARCHAR(20) NOT NULL,
        quantidade_kg  NUMERIC(12,4) NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS entradas (
        id                SERIAL PRIMARY KEY,
        sequencia         INTEGER NOT NULL UNIQUE,
        data_entrada      DATE NOT NULL,
        motivo_entrada_id INTEGER REFERENCES motivos_entrada(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_entrada (
        id         SERIAL PRIMARY KEY,
        entrada_id INTEGER NOT NULL
                   REFERENCES entradas(id) ON DELETE CASCADE,
        produto_id INTEGER REFERENCES produtos(id),
        quantidade NUMERIC(12,4) NOT NULL DEFAULT 0,
        custo      NUMERIC(12,4) NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS alteracoes_custo (
        id             SERIAL PRIMARY KEY,
        produto_id     INTEGER NOT NULL REFERENCES produtos(id),
        custo_anterior NUMERIC(12,4),
        custo_novo     NUMERIC(12,4),
        origem         VARCHAR(20) NOT NULL DEFAULT 'entrada',
        entrada_id     INTEGER REFERENCES entradas(id),
        data_alteracao TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    # índices de apoio (pesquisas e kardex)
    """
    CREATE INDEX IF NOT EXISTS idx_itens_entrada_produto
        ON itens_entrada (produto_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_entradas_data
        ON entradas (data_entrada)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_itens_ficha_ficha
        ON itens_ficha_tecnica (ficha_id)
    """,
)


def criar_schema() -> None:
    """Cria tabelas/índices que não existirem (idempotente)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for comando in _COMANDOS:
                    cur.execute(comando)
    finally:
        conn.close()
    logger.info("Schema verificado (%s comandos)", len(_COMANDOS))
