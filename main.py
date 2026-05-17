import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Iniciando aplicación...")

    # 1. Base de datos (siempre requerida)
    from src.core.database import init_db
    await init_db()
    logger.info("Base de datos inicializada")

    # 2. RabbitMQ (opcional hasta tener EC2)
    rabbitmq_available = False
    try:
        from src.core.rabbitmq.connection import rabbitmq
        await rabbitmq.connect()

        from src.core.rabbitmq.exchanges import exchange_manager
        await exchange_manager.setup()

        from src.core.database import AsyncSessionLocal
        from src.core.rabbitmq.consumer import consumer
        from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository
        from src.services.fermentation.infrastructure.event_consumer import (
            fermentation_event_consumer,
        )
        from src.services.notifications.application.usecase.send_notification_use_case import (
            SendNotificationUseCase,
        )
        from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository
        from src.services.sensors.application.usecase.save_reading_use_case import (
            SaveReadingUseCase,
        )
        from src.services.sensors.infrastructure.adapters.MySQL import SensorRepository

        fermentation_repo = FermentationRepository(AsyncSessionLocal)

        consumer.set_dependencies(
            save_reading_use_case=SaveReadingUseCase(
                SensorRepository(AsyncSessionLocal)
            ),
            send_notification_use_case=SendNotificationUseCase(
                NotificationRepository(AsyncSessionLocal)
            ),
            fermentation_repository=fermentation_repo,
        )

        fermentation_event_consumer.set_dependencies(
            fermentation_repository=fermentation_repo,
        )

        from src.core.threads.sensor_thread_manager import thread_manager
        from src.services.sensors.infrastructure.adapters.sensor_thread import SensorThread
        thread_manager.set_thread_class(SensorThread)

        await consumer.start()
        await fermentation_event_consumer.start()

        rabbitmq_available = True
        logger.info("RabbitMQ conectado y consumers iniciados")

    except Exception as e:
        logger.warning(
            f"RabbitMQ no disponible, continuando sin broker: {e}\n"
            "Los endpoints REST y WebSocket funcionan normalmente.\n"
            "Los datos de sensores en tiempo real estarán deshabilitados."
        )

    logger.info("Aplicación lista")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Cerrando aplicación...")

    if rabbitmq_available:
        from src.core.rabbitmq.connection import rabbitmq
        from src.core.rabbitmq.consumer import consumer
        from src.core.threads.sensor_thread_manager import thread_manager
        from src.services.fermentation.infrastructure.event_consumer import (
            fermentation_event_consumer,
        )

        await consumer.stop()
        await fermentation_event_consumer.stop()
        thread_manager.stop_all()
        await rabbitmq.disconnect()
        logger.info("RabbitMQ desconectado")

    logger.info("Aplicación cerrada correctamente")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sensor DB Backend",
    description="API para monitoreo de fermentación con ESP32",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from src.services.announcements.infrastructure.routes.router import router as announcements_router
from src.services.auth.infrastructure.routes.oauth_callbacks import router as oauth_callbacks_router
from src.services.auth.infrastructure.routes.router import router as auth_router
from src.services.circuits.infrastructure.routes.router import router as circuits_router
from src.services.circuits.infrastructure.routes.websocket import router as circuits_ws_router
from src.services.fermentation.infrastructure.routes.router import router as fermentation_router
from src.services.formula.infrastructure.routes.router import router as formula_router
from src.services.notifications.infrastructure.routes.router import router as notifications_router
from src.services.notifications.infrastructure.routes.websocket import (
    router as notifications_ws_router,
)
from src.services.sensors.infrastructure.routes.router import router as sensors_router
from src.services.sensors.infrastructure.routes.websocket import router as sensors_ws_router
from src.services.users.infrastructure.routes.router import router as users_router

app.include_router(auth_router,             prefix="/api/auth",          tags=["Auth"])
app.include_router(oauth_callbacks_router,  prefix="/auth",              tags=["Auth OAuth"])
app.include_router(users_router,            prefix="/api/users",         tags=["Users"])
app.include_router(circuits_router,         prefix="/api/circuits",      tags=["Circuits"])
app.include_router(circuits_ws_router,      prefix="",                   tags=["Circuits WS"])
app.include_router(sensors_router,          prefix="/api/sensors",       tags=["Sensors"])
app.include_router(sensors_ws_router,       prefix="",                   tags=["Sensors WS"])
app.include_router(fermentation_router,     prefix="/api/fermentation",  tags=["Fermentation"])
app.include_router(notifications_router,    prefix="/api/notifications", tags=["Notifications"])
app.include_router(notifications_ws_router, prefix="",                   tags=["Notifications WS"])
app.include_router(formula_router,          prefix="/api/formula",       tags=["Formula"])
app.include_router(announcements_router,    prefix="/api/announcements", tags=["Announcements"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    from src.core.rabbitmq.connection import rabbitmq
    rabbit_status = "connected"
    try:
        if rabbitmq._connection is None or rabbitmq._connection.is_closed:
            rabbit_status = "disconnected"
    except Exception:
        rabbit_status = "disconnected"

    return {
        "status":   "ok",
        "database": "connected",
        "rabbitmq": rabbit_status,
    }