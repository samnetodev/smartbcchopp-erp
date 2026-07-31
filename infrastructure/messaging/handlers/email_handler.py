from core.domain.events.order_placed import OrderPlaced


async def send_order_confirmation_email(event: OrderPlaced) -> None: ...
