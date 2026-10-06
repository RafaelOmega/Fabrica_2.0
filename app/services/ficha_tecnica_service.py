# -*- coding: utf-8 -*-
"""Service de fichas técnicas: regras de negócio."""
from app.models.ficha_tecnica import FichaTecnica
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.repositories.entrada_repository import EntradaRepository
from app.repositories.saida_repository import SaidaRepository
from app.utils.logger import get_logger

logger = get_logger("ficha_tecnica_service")


class FichaTecnicaService:

    def __init__(self):
        self._repo = FichaTecnicaRepository()
        self._entrada_repo = EntradaRepository()
        self._saida_repo = SaidaRepository()

    def salvar(self, ficha: FichaTecnica) -> FichaTecnica:
        return self._repo.inserir(ficha)

    def atualizar(self, ficha: FichaTecnica) -> bool:
        return self._repo.atualizar(ficha)

    def excluir(self, ficha_id: int) -> bool:
        return self._repo.excluir(ficha_id)

    def buscar_por_id(self, ficha_id: int) -> FichaTecnica | None:
        return self._repo.buscar_por_id(ficha_id)

    def pesquisar(self, filtro: str = "") -> list[FichaTecnica]:
        return self._repo.pesquisar(filtro)

    def buscar_por_produto(self, produto_id: int) -> FichaTecnica | None:
        return self._repo.buscar_por_produto(produto_id)

    # ---------------- edição com movimentação ----------------

    def tem_movimentacao(self, ficha_id: int) -> bool:
        """A ficha já foi usada em produção ou em venda?

        Produção: entradas com o produto acabado e motivo baixa_producao.
        Venda: saídas com o produto acabado (mão de obra derivada da ficha).
        """
        ficha = self._repo.buscar_por_id(ficha_id)
        if ficha is None or ficha.produto_id is None:
            return False
        produto_id = ficha.produto_id
        if self._entrada_repo.entradas_de_producao(produto_id):
            return True
        return bool(self._saida_repo.saidas_com_produto(produto_id))

    def corrigir_lancamentos(self, ficha: FichaTecnica) -> tuple[int, int]:
        """Atualiza a ficha e recalcula os lançamentos já efetuados.

        Corrige, com as fichas vigentes:
          - entradas de produção: baixas (kardex 'S') e custo do acabado
          - saídas: mão de obra proporcional (itens_saida_mao_obra)
        Devolve (entradas corrigidas, saídas corrigidas).
        """
        ficha_salva = self._repo.buscar_por_id(ficha.id) if ficha.id else None
        produto_id = (ficha_salva.produto_id if ficha_salva
                      else ficha.produto_id)
        self._repo.atualizar(ficha)
        entradas = saidas = 0
        if produto_id is not None:
            for entrada_id in self._entrada_repo.entradas_de_producao(
                    produto_id):
                if self._entrada_repo.recalcular_baixas(entrada_id):
                    entradas += 1
            for saida_id in self._saida_repo.saidas_com_produto(produto_id):
                if self._saida_repo.recalcular_mao_obra(saida_id):
                    saidas += 1
        logger.info("Lançamentos corrigidos pela ficha id=%s: "
                    "%s entrada(s), %s saída(s)",
                    ficha.id, entradas, saidas)
        return entradas, saidas
