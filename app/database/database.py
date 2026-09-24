# -*- coding: utf-8 -*-
"""Configuração da conexão com PostgreSQL.

Lê as credenciais das variáveis de ambiente do Windows:
DB_HOST, DB_NAME4, DB_PASSWORD, DB_PORT, DB_USER
"""
import os

import psycopg2

from app.utils.logger import get_logger

logger = get_logger("database")


def _config() -> dict:
    return {
        "host": os.getenv("DB_HOST", ""),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME4", ""),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def get_connection():
    """Retorna uma conexão ativa com o PostgreSQL."""
    cfg = _config()
    if not cfg["host"] or not cfg["dbname"] or not cfg["user"]:
        raise RuntimeError(
            "Variáveis de ambiente do banco não configuradas "
            "(DB_HOST, DB_NAME4, DB_USER)."
        )

    logger.info("Conectando ao banco %s em %s", cfg["dbname"], cfg["host"])
    return psycopg2.connect(**cfg)
