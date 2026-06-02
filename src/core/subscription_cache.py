import threading
import time


class _TTLCache:
    """
    Caché en memoria con TTL para suscripciones de usuario.
    Thread-safe — funciona desde asyncio y threads del sistema operativo.
    """

    def __init__(self, ttl: int = 300):
        self._data: dict[int, tuple[object, float]] = {}
        self._ttl  = ttl
        self._lock = threading.Lock()

    def get(self, user_id: int) -> object | None:
        with self._lock:
            entry = self._data.get(user_id)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._data[user_id]
                return None
            return value

    def set(self, user_id: int, value: object) -> None:
        with self._lock:
            self._data[user_id] = (value, time.monotonic() + self._ttl)

    def invalidate(self, user_id: int) -> None:
        with self._lock:
            self._data.pop(user_id, None)


# TTL de 5 minutos — balance entre frescura y ahorro de queries a MySQL
subscription_cache = _TTLCache(ttl=300)
