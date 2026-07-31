"""
Camada de Serviços (Service Layer).

Re-exporta os use cases da camada de aplicação como serviços.
Atua como fachada entre a API e os casos de uso.

Exemplo:
    from services import CreateOrderService
    service = CreateOrderService(uow=uow)
    result = await service.execute(data)
"""
