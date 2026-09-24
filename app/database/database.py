# -*- coding: utf-8 -*-
"""Configuração da conexão com o banco de dados.

TODO: preencher CONFIG quando as informações do banco forem fornecidas.
"""
from app.utils.logger import get_logger

logger = get_logger("database")

CONFIG = {
    "driver": "",   # ex.: "mysql+pymysql", "postgresql", "mssql+pyodbc", "sqlite"
    "host": "",
    "porta": "",
    "banco": "",
    "usuario": "",
    "senha": "",
}


def get_connection():
    """Retorna uma conexão ativa com o banco."""
    raise NotImplementedError(
        "Conexão ainda não configurada. Preencha app/database.py "
        "com os dados do banco."
    )
