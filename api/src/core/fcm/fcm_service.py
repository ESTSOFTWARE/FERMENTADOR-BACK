"""
Notificaciones push por FCM (Firebase Cloud Messaging).

- Guarda el token del dispositivo por usuario.
- Envía push a todos los dispositivos de un usuario.

El envío es best-effort y está GUARDADO: si `FIREBASE_CREDENTIALS_JSON` no está
configurado, no hace nada (no rompe el flujo de notificaciones).
"""
import asyncio
import json
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.services.notifications.infrastructure.adapters.postgres import DeviceTokenModel

logger = logging.getLogger(__name__)

_app = None
_init_tried = False


def _ensure_app():
    """Inicializa firebase-admin una sola vez. None si no hay credenciales."""
    global _app, _init_tried
    if _app is not None:
        return _app
    if _init_tried:
        return None
    _init_tried = True

    creds = settings.FIREBASE_CREDENTIALS_JSON
    if not creds:
        logger.info("[fcm] FIREBASE_CREDENTIALS_JSON no configurado; push deshabilitado")
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(json.loads(creds))
        _app = firebase_admin.initialize_app(cred)
        logger.info("[fcm] firebase-admin inicializado")
        return _app
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[fcm] no se pudo inicializar firebase-admin: {e}")
        return None


async def save_device_token(user_id: int, token: str, platform: str = "android") -> None:
    """Upsert del token (un token = un dispositivo; se reasigna al usuario actual)."""
    async with AsyncSessionLocal() as session:
        stmt = (
            pg_insert(DeviceTokenModel)
            .values(user_id=user_id, token=token, platform=platform)
            .on_conflict_do_update(
                index_elements=[DeviceTokenModel.token],
                set_={"user_id": user_id, "platform": platform},
            )
        )
        await session.execute(stmt)
        await session.commit()


async def _get_user_tokens(user_id: int) -> list[str]:
    async with AsyncSessionLocal() as session:
        rows = (
            await session.execute(
                select(DeviceTokenModel.token).where(DeviceTokenModel.user_id == user_id)
            )
        ).scalars().all()
        return list(rows)


async def get_all_registered_user_ids() -> list[int]:
    """Devuelve los user_ids distintos que tienen al menos un token registrado."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import distinct
        rows = (
            await session.execute(
                select(distinct(DeviceTokenModel.user_id))
            )
        ).scalars().all()
        return list(rows)


async def _get_tokens_for_users(user_ids: list[int]) -> list[str]:
    if not user_ids:
        return []
    async with AsyncSessionLocal() as session:
        rows = (
            await session.execute(
                select(DeviceTokenModel.token).where(
                    DeviceTokenModel.user_id.in_(user_ids)
                )
            )
        ).scalars().all()
        return list(rows)


async def send_push_to_user(
    user_id: int,
    title: str,
    body: str,
    data: dict | None = None,
) -> None:
    """Envía push FCM a todos los dispositivos del usuario. No rompe si falla."""
    await send_push_to_users([user_id], title=title, body=body, data=data)


async def send_push_to_users(
    user_ids: list[int],
    title: str,
    body: str,
    data: dict | None = None,
) -> None:
    """Envía push FCM a todos los dispositivos de una lista de usuarios en un solo multicast."""
    if _ensure_app() is None:
        return
    tokens = await _get_tokens_for_users(user_ids)
    if not tokens:
        logger.warning("[fcm] Sin tokens registrados para user_ids=%s — push omitido", user_ids)
        return
    try:
        from firebase_admin import messaging

        # FCM multicast acepta hasta 500 tokens por llamada.
        CHUNK = 500
        for i in range(0, len(tokens), CHUNK):
            chunk = tokens[i : i + CHUNK]
            message = messaging.MulticastMessage(
                tokens=chunk,
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                android=messaging.AndroidConfig(priority="high"),
            )
            batch = await asyncio.to_thread(messaging.send_each_for_multicast, message)
            logger.warning("[fcm] Batch enviado — success=%s failure=%s tokens=%s",
                           batch.success_count, batch.failure_count, len(chunk))
            for resp in batch.responses:
                if not resp.success:
                    logger.warning("[fcm] Token falló: %s", resp.exception)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[fcm] error enviando push a {len(user_ids)} usuarios: {e}")
