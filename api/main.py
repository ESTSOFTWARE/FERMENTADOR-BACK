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
_AUTO_STOP_INTERVAL_SECONDS = 60  # revisa fermentaciones vencidas cada minuto


async def _run_warning_email_task() -> None:
    """Envía correos de advertencia a usuarios cuyas cuentas vencen en 2 días."""
    await asyncio.sleep(10)  # breve espera para que la BD esté lista
    while True:
        try:
            from src.core.database import AsyncSessionLocal
            from src.services.users.application.usecase.send_warning_email_use_case import (
                SendWarningEmailUseCase,
            )
            from src.services.users.infrastructure.adapters.postgres import UserRepository

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
            from src.services.users.infrastructure.adapters.postgres import UserRepository

            count = await DeactivateExpiredUsersUseCase(UserRepository(AsyncSessionLocal)).execute()
            if count:
                logger.info(f"[Cleanup] {count} cuenta(s) desactivada(s) por no vincular circuito")
        except Exception as e:
            logger.error(f"[Cleanup] Error en tarea de desactivación: {e}")
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)


async def _run_auto_stop_fermentations_task() -> None:
    await asyncio.sleep(20)  # breve espera para que la BD esté lista
    while True:
        try:
            from src.core.database import AsyncSessionLocal
            from src.services.fermentation.application.usecase.auto_stop_expired_fermentations_use_case import (
                AutoStopExpiredFermentationsUseCase,
            )
            from src.services.fermentation.infrastructure.adapters.postgres import (
                FermentationRepository,
            )

            count = await AutoStopExpiredFermentationsUseCase(
                FermentationRepository(AsyncSessionLocal)
            ).execute()
            if count:
                logger.info(f"[AutoStop] {count} fermentación(es) detenida(s) por fin programado")
        except Exception as e:
            logger.error(f"[AutoStop] Error en tarea de auto-detención: {e}")
        await asyncio.sleep(_AUTO_STOP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Iniciando aplicación...")

    # 1. Base de datos (siempre requerida)
    from src.core.database import init_db
    await init_db()
    logger.info("Base de datos inicializada")

    # 2. RabbitMQ (opcional hasta tener broker)
    rabbitmq_available = False
    try:
        from src.core.rabbitmq.connection import rabbitmq
        # Timeout para no bloquear el arranque si el broker no responde
        # (ej. puerto firewall'd que da ETIMEDOUT en vez de refused).
        await asyncio.wait_for(rabbitmq.connect(), timeout=8)

        from src.core.rabbitmq.exchanges import exchange_manager
        await exchange_manager.setup()

        from src.core.database import AsyncSessionLocal
        from src.core.rabbitmq.consumer import consumer
        from src.services.fermentation.infrastructure.adapters.postgres import (
            FermentationRepository,
        )
        from src.services.fermentation.infrastructure.event_consumer import (
            fermentation_event_consumer,
        )
        from src.services.notifications.application.usecase.send_notification_use_case import (
            SendNotificationUseCase,
        )
        from src.services.notifications.infrastructure.adapters.postgres import (
            NotificationRepository,
        )
        from src.services.sensors.application.usecase.save_reading_use_case import (
            SaveReadingUseCase,
        )
        from src.services.sensors.infrastructure.adapters.postgres import SensorRepository

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

    # 5. Tarea periódica de auto-detención de fermentaciones vencidas (scheduled_end)
    auto_stop_task = asyncio.create_task(_run_auto_stop_fermentations_task())
    logger.info("Tarea de auto-detención de fermentaciones iniciada")

    logger.info("Aplicación lista")
    yield

    warning_email_task.cancel()
    cleanup_task.cancel()
    auto_stop_task.cancel()
    try:
        await warning_email_task
    except asyncio.CancelledError:
        pass
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    try:
        await auto_stop_task
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
    allow_origins=settings.allowed_origins,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from src.services.announcements.infrastructure.routes.router import router as announcements_router
from src.services.auth.infrastructure.routes.oauth_callbacks import router as oauth_callbacks_router
from src.services.auth.infrastructure.routes.router import router as auth_router
from src.services.auth.infrastructure.routes.session_websocket import router as session_ws_router
from src.services.billing.infrastructure.routes.router import router as billing_router
from src.services.categories.infrastructure.routes.router import router as categories_router
from src.services.chat.infrastructure.routes.router import router as chat_router
from src.services.chat.infrastructure.routes.websocket import router as chat_ws_router
from src.services.circuits.infrastructure.routes.router import router as circuits_router
from src.services.circuits.infrastructure.routes.websocket import router as circuits_ws_router
from src.services.fermentadores.infrastructure.routes.router import router as fermentadores_router
from src.services.fermentation.infrastructure.routes.router import router as fermentation_router
from src.services.formula.infrastructure.routes.router import router as formula_router
from src.services.groups.infrastructure.routes.router import router as groups_router
from src.services.notifications.infrastructure.routes.router import router as notifications_router
from src.services.notifications.infrastructure.routes.websocket import (
    router as notifications_ws_router,
)
from src.services.product_benefits.infrastructure.routes.router import router as benefits_router
from src.services.product_includes.infrastructure.routes.router import router as includes_router
from src.services.product_reviews.infrastructure.routes.router import router as reviews_router
from src.services.product_specifications.infrastructure.routes.router import (
    router as specifications_router,
)
from src.services.products.infrastructure.routes.router import router as products_router
from src.services.sensors.infrastructure.routes.router import router as sensors_router
from src.services.sensors.infrastructure.routes.websocket import router as sensors_ws_router
from src.services.support.infrastructure.routes.router import router as support_router
from src.services.support_chat.infrastructure.routes.router import router as support_chat_router
from src.services.support_chat.infrastructure.routes.websocket import (
    router as support_chat_ws_router,
)
from src.services.users.infrastructure.routes.router import router as users_router

app.include_router(auth_router,             prefix="/api/auth",          tags=["Auth"])
app.include_router(session_ws_router,       prefix="",                   tags=["Session WS"])
app.include_router(oauth_callbacks_router,  prefix="/auth",              tags=["Auth OAuth"])
app.include_router(users_router,            prefix="/api/users",         tags=["Users"])
app.include_router(categories_router,       prefix="/api/categories",                              tags=["Categories"])
app.include_router(products_router,         prefix="/api/products",                                tags=["Products"])
app.include_router(benefits_router,         prefix="/api/products/{product_id}/benefits",          tags=["Product Benefits"])
app.include_router(specifications_router,   prefix="/api/products/{product_id}/specifications",    tags=["Product Specifications"])
app.include_router(includes_router,         prefix="/api/products/{product_id}/includes",          tags=["Product Includes"])
app.include_router(reviews_router,          prefix="/api/products/{product_id}/reviews",           tags=["Product Reviews"])
app.include_router(circuits_router,         prefix="/api/circuits",      tags=["Circuits"])
app.include_router(fermentadores_router,    prefix="/api/fermentadores", tags=["Fermentadores"])
app.include_router(circuits_ws_router,      prefix="",                   tags=["Circuits WS"])
app.include_router(sensors_router,          prefix="/api/sensors",       tags=["Sensors"])
app.include_router(sensors_ws_router,       prefix="",                   tags=["Sensors WS"])
app.include_router(fermentation_router,     prefix="/api/fermentation",  tags=["Fermentation"])
app.include_router(notifications_router,    prefix="/api/notifications", tags=["Notifications"])
app.include_router(notifications_ws_router, prefix="",                   tags=["Notifications WS"])
app.include_router(formula_router,          prefix="/api/formula",       tags=["Formula"])
app.include_router(announcements_router,    prefix="/api/announcements", tags=["Announcements"])
app.include_router(groups_router,           prefix="/api/groups",        tags=["Groups"])
app.include_router(support_router,          prefix="/api/support",       tags=["Support"])
app.include_router(billing_router,          prefix="/api/billing",       tags=["Billing"])
app.include_router(chat_router,             prefix="/api/chat",          tags=["Chat"])
app.include_router(chat_ws_router,          prefix="",                   tags=["Chat WS"])
app.include_router(support_chat_router,     prefix="/api/support-chat",  tags=["Support Chat"])
app.include_router(support_chat_ws_router,  prefix="",                   tags=["Support Chat WS"])


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

from fastapi.responses import PlainTextResponse

GET_BOT_ROUTES = [
    "/console/", "/server", "/server-status", "/about", "/login.action",
    "/___proxy_subdomain_whm/login", "/___proxy_subdomain_cpanel", "/v2/_catalog",
    "/.DS_Store", "/.env", "/ecp/Current/exporttool/microsoft.exchange.ediscovery.exporttool.application",
    "/.git/config", "/s/7393e26343e26343e29363/_/;/META-INF/maven/com.atlassian.jira/jira-webapp-dist/pom.properties",
    "/config.json", "/telescope/requests", "/version", "/info.php", "/.well-known/security.txt",
    "/actuator/env", "/trace.axd", "/@vite/env", "/.vscode/sftp.json", "/debug/default/view",
    "/.git/HEAD", "/.env.production", "/.env.local", "/.env.development", "/.env.bak",
    "/.env.backup", "/robots.txt", "/sitemap.xml", "/appsettings.json", "/secrets.json",
    "/service-account.json", "/api/config", "/api/env", "/firebase-adminsdk.json",
    "/gcp-credentials.json", "/google-credentials.json", "/credentials.json",
    "/firebase.json", "/key.json", "/keyfile.json", "/account.json"
]

POST_BOT_ROUTES = [
    "/graphql", "/api", "/api/graphql", "/graphql/api", "/api/gql"
]

async def bot_response():
    ascii_message = (
        "error: no seas pendejo no hay nada aqui ve con otro servidor\n"
        "\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣤⣶⣶⣿⣿⣿⣿⣿⣿⣶⣶⣤⣤⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡾⠛⠉⠀⠀⠀⠀⠈⠉⠛⠛⢋⣠⣤⣝⡻⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠟⠁⠀⠀⠀⠀⣀⣠⣤⣬⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡿⠃⠀⢀⣠⣤⣼⣿⣿⣿⡿⠿⢿⣿⣿⣿⣿⡘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠟⠛⠛⠛⢷⡄⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠋⠀⠀⣴⣿⣿⡟⠋⣉⣁⣀⣀⣤⣾⣿⣿⡿⠋⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⡟⠈⢻⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⢸⡇⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠁⠀⠀⠀⠈⠻⣯⣄⣀⠈⠙⠻⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠈⠻⣿⣄⠻⣿⣿⣿⡇⠀⣼⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⢿⡀⠀⠀⠀⢸⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠀⢰⣄⣀⠀⢠⣤⣀⠈⠉⠉⠀⠀⠀⠉⠁⠀⠀⣠⣴⣾⣷⣦⡀⠀⠈⢿⣿⣝⣿⣿⡇⠀⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠘⠷⣶⣶⣶⠟⠁⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⣸⣿⣿⣿⣦⠙⠻⢷⣦⣄⠀⢤⣤⣴⣶⣾⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠈⠛⠀⠙⠀⠸⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡀⠀⠛⠋⠉⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢠⣿⣿⣿⠛⠁⠀⠀⠀⠀⠈⠛⢦⠙⠿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠿⢃⣾⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⣀⠈⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⣿⣿⣷⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⣘⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⡇⠀⠀⠀⠀⠀⠀⠀⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣶⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⣀⣠⣤⣤⡄⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡇⠈⠛⠛⠛⠟⠂⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠛⠿⣿⣿⣿⠀⠀⠀⠀⠀⠀⢀⣠⣤⣶⣶⣶⣶⣦⣤⣤⣀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⣄⠈⢿⣿⡦⠀⠀⠀⣠⣾⡿⠛⠛⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢀⣿⣿⣿⣿⠿⣿⣿⡿⠛⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡶⠾⣿⣿⠀⠀⠀⠀⠀⠀⢸⣇⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠹⣦⠀⠉⠀⠀⠀⠘⠋⠁⢀⣾⣿⣿⣿⣿⠏⠛⣿⠛⠁⠀⠀⠀⠀⠈⣿⣿⡟⠁⠀⠀⠀⠀⠀⠛⠛⠛⠛⢿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⣴⡏⠁⠀⠀⠈⣿⠀⠀⠀⠀⠀⠀⠈⣿⠛⠛⠋⠙⠻⣦⠀⠀⠀⠀⠀⠀⠀⢉⢰⣤⣿⣧⣰⣧⠀⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⣼⠟⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⢀⡟⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⢿⡇⠀⠀⠀⠀⠸⣧⠀⠀⠀⠀⠀⠀⢸⣼⣿⣿⡈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⢰⣿⠀⠀⠀⠀⠀⠀⠀⠸⣿⡀⠀⠀⠀⠀⢹⣷⠶⠶⢶⣤⡀⠈⢿⡇⠙⠁⠀⠀⢰⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣇⣸⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⣼⣷⡀⠀⠀⠀⠸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠙⠃⠀⠀⠀⠀⠀⠹⣧⡀⠀⠈⢿⣆⠈⢷⡄⠀⠀⠀⣦⠙⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠻⠟⠋⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⣴⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢾⣿⣧⠀⠙⢦⡀⠀⢹⣆⠘⣷⡄⠀⠀⠀⠀⠀⠀⠀⣠⣾⠟⠿⣦⣄⡀⠀⠀⢀⣠⣶⣾⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⣾⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⣰⡟⠉⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⡆⠀⠈⠷⣤⣨⣿⠀⠙⣷⡄⠀⠀⠀⠀⠀⣰⣿⡟⠀⠀⠙⢿⣷⣶⣤⣾⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⢠⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⢀⣼⠏⠀⠀⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠈⠉⠹⣇⠀⠈⠁⠀⠀⠀⠀⢠⣿⣿⠃⠀⠀⠀⠀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⢀⣾⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⣰⣿⡇⠀⠀⠀⢻⡿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠀⠀⠘⣿⣿⣦⣤⣤⣤⣤⣤⣤⣴⠶⠿⠿⠛⠛⢻⣿⣿⡇⠀⠀⠀⣼⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⣰⣿⣿⠄⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡆⠀⠀⠀⠀⠀⢠⣿⡇⠀⠀⠀⠀⠀⢀⣾⣷⡀⠀⠀⠀⠀⠀⠀⠈⠙⠻⣿⣧⣤⣀⣀⣀⣀⣀⣀⣠⣴⣾⣿⣿⣿⠃⠀⠀⠀⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⢠⣿⠛⠀⠀⠀⠀⠀⣼⡇⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠘⢻⣿⠀⠀⠀⢀⣴⣿⣿⡟⢿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢻⣿⠀⠀⠀⢸⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⢻⡄⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢸⡇⠀⣠⣴⣿⣿⣿⣿⡇⠈⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⢿⣿⣿⣿⣿⣿⡿⠋⣰⣿⡟⠀⠀⠀⣸⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⢻⡀⠀⠀⠀⣰⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢸⣷⣾⣿⣿⣿⣿⣿⣿⣷⠀⠀⠈⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⣦⣌⣉⣁⣀⣀⣤⣴⣿⡿⠁⠀⠀⢠⣿⡟⠀⠻⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠈⣷⠀⠀⠀⠘⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⠆⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠈⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠿⠿⠟⠋⠁⠀⠀⠀⠀⣾⣿⠇⠀⠀⠙⢷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠈⠻⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⠂⠀⠀⠀⠀⠈⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠙⢷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡾⠛⠀⣾⡁⢀⡀⠀⠀⠀⠀⠹⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠈⠛⠷⣤⣄⣀⣠⣤⣤⣤⣶⡾⠛⠉⠀⠀⢰⣿⣷⣾⣿⣷⣤⣀⠀⠀⠹⣿⣿⣿⣿⣶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠘⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⣛⣿⣿⣿⣷⣦⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠙⠷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡝⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠛⠉⠉⠛⢿⣿⣿⣿⣿⣿⣿⡇⠈⠻⢿⠇⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠹⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣷⣤⣤⣶⠶⠻⠿⠿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠘⢿⣿⣦⡀⠀⠀⠀⢠⣾⣿⠿⢿⣿⣿⣿⣥⣤⣤⣤⣄⣀⠉⠙⢿⡧⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠈⢻⣿⣿⣦⣤⣴⣿⠟⠁⠀⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⣦⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⣿⡿⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠙⢿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠉⠻⣷⣄⣈⠉⠉⠛⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠛⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠀⠙⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⠾⠛⠁⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⠿⠛⣻⣆⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⡇⠀⠀⢀⣀⣠⣴⠾⠛⠉⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡿⠋⢁⣠⣾⣿⣿⣷⡀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠛⣽⣿⣿⣿⣿⣿⠛⠋⠉⠀⠀⠀⠀⠀⠀⢠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⠀⣴⣿⣿⣿⣿⡟⠛⣷⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣾⡿⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣇⣴⣿⣿⣿⠟⠉⠀⣠⣾⣷⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⡿⠛⠉⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠾⠛⠋⠁⠀⠀⠀⠀⠀⢀⣀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⡿⠁⠀⢠⣾⣿⣿⣿⣧⡀⠀⠀⠀⠈⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⡇⠀⠀⠀⢀⣀⣤⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⣀⣀⣀⣀⣠⣤⣤⣴⣿⣿⣿⣿⡄⢀⣴⣿⣿⣿⣿⣿⣿⣷⡀⠀⢀⣼⡿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠛⠛⠉⠉⠁⠀⠀⠀⠀⠀⠀⠉⠙⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⡷⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠛⠋⠉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣿⡿⠿⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⠿⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    )
    return PlainTextResponse(content=ascii_message, status_code=200)

for path in GET_BOT_ROUTES:
    app.add_api_route(path, bot_response, methods=["GET"], status_code=200, include_in_schema=False)

for path in POST_BOT_ROUTES:
    app.add_api_route(path, bot_response, methods=["POST"], status_code=200, include_in_schema=False)