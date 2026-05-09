from src.services.auth.domain.repository import IAuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter
from src.core.security import create_access_token, create_refresh_token
from src.core.exceptions import InvalidCredentialsException
from src.core.config import settings


class GoogleMobileAuthUseCase:

    def __init__(self, repository: IAuthRepository, oauth: OAuthAdapter):
        self._repo  = repository
        self._oauth = oauth

    async def execute(self, google_id_token: str) -> dict:
        try:
            payload = await self._oauth.verify_google_id_token(google_id_token)
        except Exception:
            raise InvalidCredentialsException()

        if payload.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise InvalidCredentialsException()

        email     = payload.get("email")
        google_id = payload.get("sub")

        if not email or not google_id:
            raise InvalidCredentialsException()

        # Mobile: solo login — el usuario ya debe existir en la BD
        user = await self._repo.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsException()

        if not user.oauth_google_id:
            await self._repo.link_google(user.id, google_id)

        role_name = user.role.name if user.role else "estudiante"
        jwt_data  = {"sub": str(user.id), "role": role_name, "circuit_id": user.circuit_id}

        return {
            "access_token":  create_access_token(jwt_data),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
            "token_type":    "bearer",
            "user": {
                "id":            user.id,
                "name":          user.name,
                "last_name":     user.last_name,
                "email":         user.email,
                "role":          role_name,
                "circuit_id":    user.circuit_id,
                "profile_image": user.profile_image,
            },
        }
