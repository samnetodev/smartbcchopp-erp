from decimal import Decimal

from core.domain.entities.product import Product


class PricingService:
    def calcular_preco_venda(
        self, product: Product, margem_percentual: Decimal | None = None
    ) -> Decimal:
        margem = margem_percentual or Decimal("30")
        custo = product.preco_custo
        return custo + (custo * margem / Decimal("100"))

    def aplicar_desconto_volume(self, quantidade: Decimal, preco_unitario: Decimal) -> Decimal:
        if quantidade >= Decimal("100"):
            return preco_unitario * Decimal("0.90")
        if quantidade >= Decimal("50"):
            return preco_unitario * Decimal("0.95")
        return preco_unitario
