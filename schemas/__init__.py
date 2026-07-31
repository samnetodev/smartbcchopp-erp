"""
Re-export dos schemas Pydantic para conveniência de importação.

Uso: from schemas import ProductCreate, ProductResponse

Os schemas reais estão em api.serializers para manter
a separação da Clean Architecture (Presentation Layer).
"""

from api.serializers import (
    CustomerCreate,
    CustomerResponse,
    OrderCreate,
    OrderItemSchema,
    OrderResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

__all__ = [
    "CustomerCreate",
    "CustomerResponse",
    "OrderCreate",
    "OrderItemSchema",
    "OrderResponse",
    "ProductCreate",
    "ProductResponse",
    "ProductUpdate",
]
