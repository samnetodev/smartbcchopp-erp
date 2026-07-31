from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.middlewares.error_handler import setup_error_handlers
from api.middlewares.request_id import RequestIDMiddleware
from config.logging import setup_logging
from config.settings import get_settings
from database.session import close_db_engine, get_async_session_factory
from infrastructure.automation.scheduler import SchedulerService

settings = get_settings()
setup_logging(debug=settings.DEBUG, json_format=settings.LOG_FORMAT == "json")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    session_factory = get_async_session_factory()
    scheduler = SchedulerService(session_factory)
    await scheduler.start()
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        await scheduler.stop()
        await close_db_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    setup_health_endpoint(app)
    setup_error_handlers(app)
    register_routes(app)

    return app


def setup_health_endpoint(app: FastAPI) -> None:
    @app.get("/health")
    async def health(request: Request) -> JSONResponse:
        return JSONResponse(
            content={
                "status": "ok",
                "version": "0.1.0",
                "app": settings.APP_NAME,
            }
        )


def register_routes(app: FastAPI) -> None:
    from api.routes.v1.auditoria_routes import router as auditoria_router
    from api.routes.v1.auth_routes import router as auth_router
    from api.routes.v1.automation_routes import router as automation_router
    from api.routes.v1.chopeira_routes import router as chopeira_router
    from api.routes.v1.commercial_routes import router as commercial_router
    from api.routes.v1.customer_routes import router as customer_router
    from api.routes.v1.dashboard_routes import router as dashboard_router
    from api.routes.v1.financial_routes import router as financial_router
    from api.routes.v1.fleet_routes import router as fleet_router
    from api.routes.v1.inventory_routes import router as inventory_router
    from api.routes.v1.order_routes import router as order_router
    from api.routes.v1.product_routes import router as product_router
    from api.routes.v1.supplier_routes import router as supplier_router
    from api.routes.v1.whatsapp_routes import router as whatsapp_router

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(chopeira_router, prefix="/api/v1/chopeiras", tags=["Chopeiras"])
    app.include_router(commercial_router, prefix="/api/v1/commercial", tags=["Commercial"])
    app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])
    app.include_router(customer_router, prefix="/api/v1/customers", tags=["Customers"])
    app.include_router(order_router, prefix="/api/v1/orders", tags=["Orders"])
    app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
    app.include_router(fleet_router, prefix="/api/v1/fleet", tags=["Fleet"])
    app.include_router(financial_router, prefix="/api/v1/financial", tags=["Financial"])
    app.include_router(supplier_router, prefix="/api/v1/suppliers", tags=["Suppliers"])
    app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
    app.include_router(
        automation_router, prefix="/api/v1/automation", tags=["Automation"]
    )
    app.include_router(auditoria_router, prefix="/api/v1/auditoria", tags=["Auditoria"])


app = create_app()
