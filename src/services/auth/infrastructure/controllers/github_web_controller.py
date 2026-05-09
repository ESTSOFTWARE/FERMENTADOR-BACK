import urllib.parse
from fastapi.responses import RedirectResponse
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter
from src.services.auth.application.usecase.github_web_auth_use_case import GitHubWebAuthUseCase
from src.core.database import AsyncSessionLocal
from src.core.config import settings


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
    params = urllib.parse.urlencode({
        "access_token":  result["access_token"],
        "refresh_token": result["refresh_token"],
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?{params}")
