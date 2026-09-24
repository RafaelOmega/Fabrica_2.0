# -*- coding: utf-8 -*-
"""Service de produtos: regras de negócio + acesso a dados."""
from app.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("produto_service")


class ProdutoService:
    """Operações de CRUD de produtos.

    Os controllers chamam estes métodos; a conexão vem de app/database.py.
    """

    def salvar(self, dados: dict) -> int:
        """Insere um novo produto e retorna o id criado."""
        conn = get_connection()
        # TODO: montar INSERT conforme o banco (quando configurado)
        logger.info("salvar: %s", dados.get("codigo"))
        return 0

    def atualizar(self, dados: dict) -> bool:
        """Atualiza o produto existente."""
        conn = get_connection()
        # TODO: montar UPDATE conforme o banco
        logger.info("atualizar: %s", dados.get("codigo"))
        return True

    def excluir(self, codigo: str) -> bool:
        """Remove o produto pelo código."""
        conn = get_connection()
        # TODO: montar DELETE conforme o banco
        logger.info("excluir: %s", codigo)
        return True

    def pesquisar(self, filtro: str = "") -> list:
        """Busca produtos filtrando por código/descrição."""
        conn = get_connection()
        # TODO: montar SELECT com filtro conforme o banco
        logger.info("pesquisar: %s", filtro)
        return []
