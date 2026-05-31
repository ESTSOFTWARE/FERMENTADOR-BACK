import logging
from datetime import datetime, timedelta, timezone

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)

PLAN_MAP: dict[str, dict[str, str]] = {}

_token_cache: dict[str, object] = {"token": None, "expires_at": None}


def _base_url() -> str:
    if settings.PAYPAL_MODE == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"


def _build_plan_map() -> None:
    global PLAN_MAP
    PLAN_MAP = {
        "starter":    {
            "monthly": settings.PAYPAL_PLAN_STARTER_MONTHLY,
            "annual":  settings.PAYPAL_PLAN_STARTER_ANNUAL,
        },
        "academic":   {
            "monthly": settings.PAYPAL_PLAN_ACADEMIC_MONTHLY,
            "annual":  settings.PAYPAL_PLAN_ACADEMIC_ANNUAL,
        },
        "enterprise": {
            "monthly": settings.PAYPAL_PLAN_ENTERPRISE_MONTHLY,
            "annual":  settings.PAYPAL_PLAN_ENTERPRISE_ANNUAL,
        },
    }


class PayPalAdapter:

    async def _get_token(self) -> str:
        now = datetime.now(timezone.utc)
        if _token_cache["token"] and _token_cache["expires_at"] > now:
            return _token_cache["token"]

        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{_base_url()}/v1/oauth2/token",
                auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
                data={"grant_type": "client_credentials"},
            )
            res.raise_for_status()
            data = res.json()
            _token_cache["token"]      = data["access_token"]
            _token_cache["expires_at"] = now + timedelta(seconds=data["expires_in"] - 60)
            return _token_cache["token"]

    async def _headers(self) -> dict:
        token = await self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        }

    def get_plan_id(self, plan: str, billing_cycle: str) -> str:
        if not PLAN_MAP:
            _build_plan_map()
        plan_id = PLAN_MAP.get(plan, {}).get(billing_cycle, "")
        if not plan_id:
            raise ValueError(f"PayPal Plan ID no configurado para {plan}/{billing_cycle}")
        return plan_id

    async def create_subscription(
        self,
        plan_id:    str,
        user_id:    int,
        return_url: str,
        cancel_url: str,
    ) -> str:
        headers = await self._headers()
        payload = {
            "plan_id": plan_id,
            "custom_id": str(user_id),
            "application_context": {
                "brand_name":          "Nich-Ká",
                "locale":              "es-MX",
                "shipping_preference": "NO_SHIPPING",
                "user_action":         "SUBSCRIBE_NOW",
                "return_url":          return_url,
                "cancel_url":          cancel_url,
            },
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{_base_url()}/v1/billing/subscriptions",
                headers=headers,
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
            logger.info(f"[PayPal] Suscripción creada: {data['id']}")
            return data["id"]

    async def get_subscription(self, subscription_id: str) -> dict:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{_base_url()}/v1/billing/subscriptions/{subscription_id}",
                headers=headers,
            )
            res.raise_for_status()
            return res.json()

    async def cancel_subscription(self, subscription_id: str) -> None:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{_base_url()}/v1/billing/subscriptions/{subscription_id}/cancel",
                headers=headers,
                json={"reason": "Cancelado por el usuario"},
            )
            res.raise_for_status()

    async def create_order(
        self,
        amount:      str,
        currency:    str,
        description: str,
        return_url:  str,
        cancel_url:  str,
    ) -> str:
        headers = await self._headers()
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount":      {"currency_code": currency, "value": amount},
                "description": description,
            }],
            "application_context": {
                "brand_name":          "Nich-Ká",
                "locale":              "es-MX",
                "shipping_preference": "NO_SHIPPING",
                "return_url":          return_url,
                "cancel_url":          cancel_url,
            },
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{_base_url()}/v2/checkout/orders",
                headers=headers,
                json=payload,
            )
            res.raise_for_status()
            return res.json()["id"]

    async def capture_order(self, order_id: str) -> dict:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{_base_url()}/v2/checkout/orders/{order_id}/capture",
                headers=headers,
                json={},
            )
            res.raise_for_status()
            return res.json()

    async def generate_client_token(self) -> str:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{_base_url()}/v1/identity/generate-token",
                headers=headers,
                json={},
            )
            res.raise_for_status()
            return res.json()["client_token"]
