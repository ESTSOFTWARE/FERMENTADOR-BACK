from fastapi import APIRouter

from src.services.auth.infrastructure.controllers.github_web_controller import github_callback
from src.services.auth.infrastructure.controllers.google_web_controller import google_callback

router = APIRouter()


@router.get("/google/callback", summary="Callback Google OAuth → redirige al frontend con tokens")
async def google_callback_route(code: str):
    return await google_callback(code)


@router.get("/github/callback", summary="Callback GitHub OAuth → redirige al frontend con tokens")
async def github_callback_route(code: str):
    return await github_callback(code)
