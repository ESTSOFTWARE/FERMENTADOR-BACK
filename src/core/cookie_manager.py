from fastapi import Response

from src.core.config import settings

ACCESS_TOKEN_COOKIE  = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    _domain = settings.COOKIE_DOMAIN or None
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=_domain,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
        domain=_domain,
    )


def set_access_cookie(response: Response, access_token: str) -> None:
    _domain = settings.COOKIE_DOMAIN or None
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=_domain,
    )


def clear_auth_cookies(response: Response) -> None:
    _domain = settings.COOKIE_DOMAIN or None
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE,  path="/", domain=_domain)
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE, path="/", domain=_domain)
