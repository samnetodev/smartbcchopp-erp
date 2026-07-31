from decimal import Decimal
from typing import Any

from core.shared.base_entity import BaseEntity


class Product(BaseEntity):
    def __init__(
        self,
        codigo: str,
        nome: str,
        categoria: str,
        unidade_medida: str,
        preco_venda: Decimal,
        preco_custo: Decimal = Decimal("0"),
        ativo: bool = True,
        estoque_minimo: Decimal = Decimal("0"),
        lote_obrigatorio: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.codigo = codigo
        self.nome = nome
        self.categoria = categoria
        self.unidade_medida = unidade_medida
        self.preco_venda = preco_venda
        self.preco_custo = preco_custo
        self.ativo = ativo
        self.estoque_minimo = estoque_minimo
        self.lote_obrigatorio = lote_obrigatorio
