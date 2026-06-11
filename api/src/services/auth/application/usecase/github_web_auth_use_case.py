from src.core.email.email_service import send_welcome_email
from src.core.exceptions import InvalidCredentialsException
from src.core.security import create_access_token, create_refresh_token
from src.core.session import rotate_and_revoke
from src.services.auth.domain.repository import IAuthRepository
from src.services.auth.infrastructure.adapters.oauth_adapter import OAuthAdapter


class GitHubWebAuthUseCase:

    def __init__(self, repository: IAuthRepository, oauth: OAuthAdapter):
        self._repo  = repository
        self._oauth = oauth

    async def execute(self, code: str) -> dict:
        token_data = await self._oauth.get_github_token(code)
        access_token = token_data.get("access_token")
        if not access_token:
            raise InvalidCredentialsException()

        user_info = await self._oauth.get_github_user_info(access_token)
        github_id = str(user_info.get("id", ""))
        email     = user_info.get("email")

        if not github_id or not email:
            raise InvalidCredentialsException()

        full_name = user_info.get("name") or user_info.get("login") or ""
        parts     = full_name.split(" ", 1)
        name      = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        is_new = False
        user = await self._repo.get_user_by_github_id(github_id)
        if not user:
            user = await self._repo.get_user_by_email(email)
            if user:
                await self._repo.link_github(user.id, github_id)
                user = await self._repo.get_user_by_id(user.id)
            else:
                user = await self._repo.create_user_with_github(
                    name=name,
                    last_name=last_name,
                    email=email,
                    github_id=github_id,
                )
                is_new = True

        if not user.is_active:
            await self._repo.reactivate_user_with_notification(
                user_id=user.id,
                user_name=user.name,
                user_email=user.email,
            )
            user = await self._repo.get_user_by_id(user.id)

        if is_new:
            await send_welcome_email(to_email=user.email, name=user.name)

        role_name = user.role.name if user.role else "admin"
        sid = await rotate_and_revoke(self._repo, user.id)
        jwt_data  = {"sub": str(user.id), "role": role_name, "circuit_id": user.circuit_id, "sid": sid}

        return {
            "access_token":  create_access_token(jwt_data),
            "refresh_token": create_refresh_token({"sub": str(user.id), "sid": sid}),
            "token_type":    "bearer",
            "user": {
                "id":             user.id,
                "name":           user.name,
                "last_name":      user.last_name,
                "email":          user.email,
                "role":           role_name,
                "circuit_id":     user.circuit_id,
                "profile_image":  user.profile_image,
                "oauth_provider": "github",
            },
        }
