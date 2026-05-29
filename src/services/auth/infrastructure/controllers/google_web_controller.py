import base64
import json
import urllib.parse

from fastapi.responses import RedirectResponse

from src.core.config import settings
from src.core.cookie_manager import set_auth_cookies
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
    try:
        repo   = AuthRepository(AsyncSessionLocal)
        result = await GoogleWebAuthUseCase(repo, OAuthAdapter()).execute(code)
        user_b64 = base64.b64encode(json.dumps(result["user"]).encode()).decode()
        redirect = RedirectResponse(
            f"{settings.FRONTEND_URL}/auth/callback?user_data={urllib.parse.quote(user_b64)}",
            status_code=302,
        )
        set_auth_cookies(redirect, result["access_token"], result["refresh_token"])
        return redirect
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"[Google OAuth] Callback error: {e}")
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/login?oauth_error={error_msg}",
            status_code=302,
        )
