import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_CLEANUP_INTERVAL_SECONDS = 24 * 60 * 60  # cada 24 horas
_WARNING_EMAIL_INTERVAL_SECONDS = 12 * 60 * 60  # cada 12 horas


async def _run_warning_email_task() -> None:
    """Envía correos de advertencia a usuarios cuyas cuentas vencen en 2 días."""
    await asyncio.sleep(10)  # breve espera para que la BD esté lista
    while True:
        try:
            from src.core.database import AsyncSessionLocal
            from src.services.users.application.usecase.send_warning_email_use_case import (
                SendWarningEmailUseCase,
            )
            from src.services.users.infrastructure.adapters.MySQL import UserRepository

            count = await SendWarningEmailUseCase(UserRepository(AsyncSessionLocal)).execute()
            if count:
                logger.info(f"[Warning Email] {count} correo(s) de advertencia enviado(s)")
        except Exception as e:
            logger.error(f"[Warning Email] Error en tarea de advertencia: {e}")
        await asyncio.sleep(_WARNING_EMAIL_INTERVAL_SECONDS)


async def _run_user_cleanup_task() -> None:
    await asyncio.sleep(5)  # breve espera para que la BD esté lista
    while True:
        try:
            from src.core.database import AsyncSessionLocal
            from src.services.users.application.usecase.deactivate_expired_users_use_case import (
                DeactivateExpiredUsersUseCase,
            )
            from src.services.users.infrastructure.adapters.MySQL import UserRepository

            count = await DeactivateExpiredUsersUseCase(UserRepository(AsyncSessionLocal)).execute()
            if count:
                logger.info(f"[Cleanup] {count} cuenta(s) desactivada(s) por no vincular circuito")
        except Exception as e:
            logger.error(f"[Cleanup] Error en tarea de desactivación: {e}")
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)


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

    # 3. Tarea periódica de envío de correos de advertencia
    warning_email_task = asyncio.create_task(_run_warning_email_task())
    logger.info("Tarea de correos de advertencia iniciada")

    # 4. Tarea periódica de desactivación de cuentas sin circuito
    cleanup_task = asyncio.create_task(_run_user_cleanup_task())
    logger.info("Tarea de limpieza de cuentas iniciada")

    logger.info("Aplicación lista")
    yield

    warning_email_task.cancel()
    cleanup_task.cancel()
    try:
        await warning_email_task
    except asyncio.CancelledError:
        pass
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

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
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from src.services.announcements.infrastructure.routes.router import router as announcements_router
from src.services.auth.infrastructure.routes.oauth_callbacks import router as oauth_callbacks_router
from src.services.auth.infrastructure.routes.router import router as auth_router
from src.services.billing.infrastructure.routes.router import router as billing_router
from src.services.circuits.infrastructure.routes.router import router as circuits_router
from src.services.circuits.infrastructure.routes.websocket import router as circuits_ws_router
from src.services.fermentation.infrastructure.routes.router import router as fermentation_router
from src.services.formula.infrastructure.routes.router import router as formula_router
from src.services.groups.infrastructure.routes.router import router as groups_router
from src.services.notifications.infrastructure.routes.router import router as notifications_router
from src.services.notifications.infrastructure.routes.websocket import (
    router as notifications_ws_router,
)
from src.services.products.infrastructure.routes.router import router as products_router
from src.services.sensors.infrastructure.routes.router import router as sensors_router
from src.services.sensors.infrastructure.routes.websocket import router as sensors_ws_router
from src.services.support.infrastructure.routes.router import router as support_router
from src.services.users.infrastructure.routes.router import router as users_router

app.include_router(auth_router,             prefix="/api/auth",          tags=["Auth"])
app.include_router(oauth_callbacks_router,  prefix="/auth",              tags=["Auth OAuth"])
app.include_router(users_router,            prefix="/api/users",         tags=["Users"])
app.include_router(products_router,         prefix="/api/products",      tags=["Products"])
app.include_router(circuits_router,         prefix="/api/circuits",      tags=["Circuits"])
app.include_router(circuits_ws_router,      prefix="",                   tags=["Circuits WS"])
app.include_router(sensors_router,          prefix="/api/sensors",       tags=["Sensors"])
app.include_router(sensors_ws_router,       prefix="",                   tags=["Sensors WS"])
app.include_router(fermentation_router,     prefix="/api/fermentation",  tags=["Fermentation"])
app.include_router(notifications_router,    prefix="/api/notifications", tags=["Notifications"])
app.include_router(notifications_ws_router, prefix="",                   tags=["Notifications WS"])
app.include_router(formula_router,          prefix="/api/formula",       tags=["Formula"])
app.include_router(announcements_router,    prefix="/api/announcements", tags=["Announcements"])
app.include_router(groups_router,           prefix="/api/groups",        tags=["Groups"])
app.include_router(support_router,          prefix="/support",           tags=["Support"])
app.include_router(billing_router,          prefix="/api/billing",       tags=["Billing"])


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