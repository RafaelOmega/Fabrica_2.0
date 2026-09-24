# -*- coding: utf-8 -*-
"""Service de produtos: regras de negócio."""
from app.models.produto import Produto
from app.repositories.produto_repository import ProdutoRepository
from app.utils.logger import get_logger

logger = get_logger("produto_service")


class ProdutoService:

    def __init__(self):
        self._repo = ProdutoRepository()

    def salvar(self, dados: dict) -> Produto:
        return self._repo.inserir(Produto.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(Produto.from_dict(dados))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def buscar_por_codigo(self, codigo: str) -> Produto | None:
        return self._repo.buscar_por_codigo(codigo)

    def pesquisar(self, filtro: str = "") -> list[Produto]:
        return self._repo.pesquisar(filtro)
