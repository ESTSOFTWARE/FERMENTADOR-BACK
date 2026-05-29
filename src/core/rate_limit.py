import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

_store: dict[str, list[datetime]] = defaultdict(list)


def check_rate_limit(
    key: str,
    max_requests: int = 3,
    window_seconds: int = 300,
) -> bool:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    _store[key] = [t for t in _store[key] if t > cutoff]
    if len(_store[key]) >= max_requests:
        logger.warning(f"[RateLimit] Límite alcanzado para: {key}")
        return False
    _store[key].append(now)
    return True
