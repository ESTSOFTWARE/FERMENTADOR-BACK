import traceback

from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.get_active_fermentation_use_case import (
    GetActiveFermentationUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository


async def get_active(circuit_id, user_id=None):
    try:
        if not circuit_id and user_id is not None:
            try:
                from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
                user       = await AuthRepository(AsyncSessionLocal).get_user_by_id(user_id)
                circuit_id = getattr(user, "circuit_id", None) if user else None
            except Exception as e:
                print(f"[get_active] fallback lookup failed: {e}", flush=True)
                circuit_id = None

        print(f"[get_active] resolved circuit_id={circuit_id} user_id={user_id}", flush=True)
        session = await GetActiveFermentationUseCase(FermentationRepository(AsyncSessionLocal)).execute(circuit_id)
        print(f"[get_active] session={session}", flush=True)
        if not session:
            return None
        resp = FermentationSessionResponse.from_entity(session)
        print(f"[get_active] resp built ok: id={resp.id} status={resp.status}", flush=True)
        return resp
    except Exception as e:
        print("[get_active] EXCEPTION:", repr(e), flush=True)
        traceback.print_exc()
        raise
