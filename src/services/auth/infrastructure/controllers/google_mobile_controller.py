from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter
from src.services.auth.application.usecase.google_mobile_auth_use_case import GoogleMobileAuthUseCase
from src.services.auth.domain.dto.oauth_schema import GoogleMobileRequest
from src.core.database import AsyncSessionLocal


async def google_mobile(body: GoogleMobileRequest):
    repo = AuthRepository(AsyncSessionLocal)
    return await GoogleMobileAuthUseCase(repo, OAuthAdapter()).execute(body.id_token)
