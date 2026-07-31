
from dependency_injector import containers, providers

from config.settings import Settings
from database.session import get_async_session_factory
from infrastructure.automation.scheduler import SchedulerService
from infrastructure.cache.redis_client import RedisCacheService


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.routes.v1.auth_routes",
            "api.routes.v1.product_routes",
            "api.routes.v1.customer_routes",
            "api.routes.v1.order_routes",
            "api.routes.v1.inventory_routes",
            "api.routes.v1.vehicle_routes",
            "api.routes.v1.financial_routes",
            "api.routes.v1.commercial_routes",
            "api.routes.v1.dashboard_routes",
            "api.routes.v1.supplier_routes",
            "api.routes.v1.whatsapp_routes",
            "api.routes.v1.automation_routes",
        ]
    )

    config: providers.Singleton[Settings] = providers.Singleton(Settings)

    cache: providers.Singleton[RedisCacheService] = providers.Singleton(
        RedisCacheService,
        redis_url=config.provided.REDIS_URL,
    )

    session_factory = providers.Callable(get_async_session_factory)

    scheduler = providers.Singleton(
        SchedulerService,
        session_factory=session_factory,
    )
