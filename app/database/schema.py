# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: cada comando usa
CREATE TABLE/INDEX IF NOT EXISTS, portanto em bancos já existentes
nada é alterado; em banco novo, todas as tabelas são criadas.

A tabela movimentos_kardex recebe um espelho de cada movimento
(entradas tipo 'E' e saídas tipo 'S') e ainda um backfill idempotente
das entradas já lançadas antes da tabela existir.
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
    """
    CREATE TABLE IF NOT EXISTS movimentos_kardex (
        id             SERIAL PRIMARY KEY,
        produto_id     INTEGER NOT NULL REFERENCES produtos(id),
        data_movimento DATE NOT NULL,
        tipo           CHAR(1) NOT NULL CHECK (tipo IN ('E', 'S')),
        documento      VARCHAR(20) NOT NULL DEFAULT '',
        historico      VARCHAR(120) NOT NULL DEFAULT '',
        quantidade     NUMERIC(12,4) NOT NULL DEFAULT 0,
        custo_unitario NUMERIC(12,4),
        entrada_id     INTEGER REFERENCES entradas(id),
        saida_id       INTEGER,
        criado_em      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    # ---------------- saidas ----------------
    """
    CREATE TABLE IF NOT EXISTS saidas (
        id         SERIAL PRIMARY KEY,
        sequencia  INTEGER NOT NULL UNIQUE,
        data_saida DATE NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_saida (
        id         SERIAL PRIMARY KEY,
        saida_id   INTEGER NOT NULL
                   REFERENCES saidas(id) ON DELETE CASCADE,
        produto_id INTEGER REFERENCES produtos(id),
        quantidade NUMERIC(12,4) NOT NULL DEFAULT 0,
        custo      NUMERIC(12,4) NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_saida_mao_obra (
        id         SERIAL PRIMARY KEY,
        saida_id   INTEGER NOT NULL
                   REFERENCES saidas(id) ON DELETE CASCADE,
        produto_id INTEGER REFERENCES produtos(id),
        quantidade NUMERIC(12,4) NOT NULL DEFAULT 0,
        custo      NUMERIC(12,4) NOT NULL DEFAULT 0
    )
    """,
    """
    DO $$
    BEGIN
        ALTER TABLE movimentos_kardex
            ADD CONSTRAINT fk_kardex_saida
            FOREIGN KEY (saida_id) REFERENCES saidas(id);
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$
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
    """
    CREATE INDEX IF NOT EXISTS idx_kardex_produto_data
        ON movimentos_kardex (produto_id, data_movimento)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_kardex_entrada
        ON movimentos_kardex (entrada_id)
    """,
    # índices de apoio (saídas)
    """
    CREATE INDEX IF NOT EXISTS idx_itens_saida_saida
        ON itens_saida (saida_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_itens_saida_mao_obra_saida
        ON itens_saida_mao_obra (saida_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_kardex_saida
        ON movimentos_kardex (saida_id)
    """,
    # ---------------- unidades de medida ----------------
    """
    CREATE TABLE IF NOT EXISTS unidades_medida (
        id              SERIAL PRIMARY KEY,
        codigo          VARCHAR(20) NOT NULL UNIQUE,
        descricao       VARCHAR(120) NOT NULL,
        fator_conversao NUMERIC(12,4) NOT NULL DEFAULT 0
    )
    """,
    # ---------------- vínculo produto x unidade ----------------
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
             WHERE table_name = 'produtos' AND column_name = 'unidade'
        ) THEN
            ALTER TABLE produtos ADD COLUMN unidade VARCHAR(20);
            ALTER TABLE produtos
                ADD CONSTRAINT fk_produto_unidade
                FOREIGN KEY (unidade) REFERENCES unidades_medida(codigo);
        END IF;
    END $$
    """,
)

# Backfill idempotente: espelha entradas lançadas antes da tabela existir.
_BACKFILL_KARDEX = """
    INSERT INTO movimentos_kardex
        (produto_id, data_movimento, tipo, documento, historico,
         quantidade, custo_unitario, entrada_id)
    SELECT ie.produto_id, e.data_entrada, 'E',
           CAST(e.sequencia AS TEXT),
           COALESCE(m.descricao, ''),
           ie.quantidade, ie.custo, e.id
      FROM itens_entrada ie
      JOIN entradas e ON e.id = ie.entrada_id
      LEFT JOIN motivos_entrada m ON m.id = e.motivo_entrada_id
     WHERE ie.produto_id IS NOT NULL
       AND NOT EXISTS (
            SELECT 1 FROM movimentos_kardex mk
             WHERE mk.entrada_id = e.id
               AND mk.produto_id = ie.produto_id
               AND mk.quantidade = ie.quantidade
       )
"""


def criar_schema() -> None:
    """Cria tabelas/índices que não existirem (idempotente)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for comando in _COMANDOS:
                    cur.execute(comando)
                cur.execute(_BACKFILL_KARDEX)
    finally:
        conn.close()
    logger.info("Schema verificado (%s comandos)", len(_COMANDOS))
