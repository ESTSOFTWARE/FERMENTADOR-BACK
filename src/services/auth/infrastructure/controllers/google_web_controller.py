import urllib.parse

from fastapi.responses import RedirectResponse

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.services.auth.application.usecase.google_web_auth_use_case import GoogleWebAuthUseCase
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter


async def google_redirect():
    params = {
        "client_id":     settings.GOOGLE_CLIENT_ID,
        "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


async def google_callback(code: str):
    repo   = AuthRepository(AsyncSessionLocal)
    result = await GoogleWebAuthUseCase(repo, OAuthAdapter()).execute(code)
    params = urllib.parse.urlencode({
        "access_token":  result["access_token"],
        "refresh_token": result["refresh_token"],
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?{params}")
