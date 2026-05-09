import httpx
from src.core.config import settings


class OAuthAdapter:

    async def get_google_token(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code":          code,
                    "client_id":     settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
                    "grant_type":    "authorization_code",
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()

    async def verify_google_id_token(self, id_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_github_token(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code":          code,
                    "client_id":     settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "redirect_uri":  settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_github_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept":        "application/vnd.github.v3+json",
                },
            )
            resp.raise_for_status()
            user = resp.json()

            # GitHub users can have private emails — fetch separately if needed
            if not user.get("email"):
                email_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept":        "application/vnd.github.v3+json",
                    },
                )
                if email_resp.status_code == 200:
                    emails = email_resp.json()
                    primary = next(
                        (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                        None,
                    )
                    user["email"] = primary

            return user
