from core.domain.entities.customer import Customer


class CreditAnalysisService:
    def verificar_limite(self, customer: Customer, valor_pedido: float) -> bool:
        return customer.limite_credito >= valor_pedido

    def liberar_credito(self, customer: Customer, valor: float) -> Customer:
        customer.limite_credito += valor
        return customer
