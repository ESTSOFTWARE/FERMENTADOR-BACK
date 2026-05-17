import base64
import json
import urllib.parse

from fastapi.responses import RedirectResponse

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.services.auth.application.usecase.github_web_auth_use_case import GitHubWebAuthUseCase
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter


async def github_redirect():
    params = {
        "client_id":    settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope":        "user:email",
    }
    url = "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


async def github_callback(code: str):
    repo   = AuthRepository(AsyncSessionLocal)
    result = await GitHubWebAuthUseCase(repo, OAuthAdapter()).execute(code)
    user_b64 = base64.urlsafe_b64encode(json.dumps(result["user"]).encode()).decode()
    params = urllib.parse.urlencode({
        "access_token":  result["access_token"],
        "refresh_token": result["refresh_token"],
        "user_data":     user_b64,
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?{params}")
