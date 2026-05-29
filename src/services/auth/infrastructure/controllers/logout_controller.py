from fastapi import Response

from src.core.cookie_manager import clear_auth_cookies


async def logout(response: Response) -> dict:
    clear_auth_cookies(response)
    return {"message": "Sesión cerrada correctamente"}
