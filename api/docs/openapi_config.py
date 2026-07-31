from typing import Any


def get_openapi_config() -> dict[str, Any]:
    return {
        "title": "SmartBcChopp ERP API",
        "version": "0.1.0",
        "description": (
            "API do ERP Inteligente para Distribuidora de Chope, Carvão e Transporte.\n\n"
            "## Módulos\n"
            "- **Auth** - Autenticação e autorização JWT\n"
            "- **Catalog** - Produtos, famílias e tabela de preços\n"
            "- **Sales** - Pedidos e orçamentos\n"
            "- **Inventory** - Estoque e movimentações\n"
            "- **Transportation** - Veículos, motoristas e entregas\n"
            "- **Financial** - Contas a receber/pagar e fluxo de caixa\n"
            "- **CRM** - Clientes e análise de crédito\n"
            "- **Suppliers** - Fornecedores e compras\n"
        ),
    }
