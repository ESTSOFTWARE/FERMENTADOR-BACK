from src.core.email.email_service import send_welcome_email
from src.core.exceptions import InvalidCredentialsException
from src.core.security import create_access_token, create_refresh_token
from src.services.auth.domain.repository import IAuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter


class GoogleWebAuthUseCase:

    def __init__(self, repository: IAuthRepository, oauth: OAuthAdapter):
        self._repo  = repository
        self._oauth = oauth

    async def execute(self, code: str) -> dict:
        token_data = await self._oauth.get_google_token(code)
        access_token = token_data.get("access_token")
        if not access_token:
            raise InvalidCredentialsException()

        user_info = await self._oauth.get_google_user_info(access_token)
        google_id = user_info.get("id")
        email     = user_info.get("email")
        name      = user_info.get("given_name") or ""
        last_name = user_info.get("family_name") or ""

        if not google_id or not email:
            raise InvalidCredentialsException()

        is_new = False
        user = await self._repo.get_user_by_google_id(google_id)
        if not user:
            user = await self._repo.get_user_by_email(email)
            if user:
                await self._repo.link_google(user.id, google_id)
                user = await self._repo.get_user_by_id(user.id)
            else:
                user = await self._repo.create_user_with_google(
                    name=name,
                    last_name=last_name,
                    email=email,
                    google_id=google_id,
                )
                is_new = True

        if not user.is_active:
            await self._repo.reactivate_user(user.id)
            user = await self._repo.get_user_by_id(user.id)

        if is_new:
            await send_welcome_email(to_email=user.email, name=user.name)

        role_name  = user.role.name if user.role else "admin"
        jwt_data   = {"sub": str(user.id), "role": role_name, "circuit_id": user.circuit_id}

        return {
            "access_token":  create_access_token(jwt_data),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
            "token_type":    "bearer",
            "user": {
                "id":             user.id,
                "name":           user.name,
                "last_name":      user.last_name,
                "email":          user.email,
                "role":           role_name,
                "circuit_id":     user.circuit_id,
                "profile_image":  user.profile_image,
                "oauth_provider": "google",
            },
        }
