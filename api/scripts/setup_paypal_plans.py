"""
Ejecutar UNA sola vez para crear los productos y planes de suscripción en PayPal.
Copia los IDs generados en el .env

    python scripts/setup_paypal_plans.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("PAYPAL_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
MODE          = os.getenv("PAYPAL_MODE", "sandbox")

BASE_URL = "https://api-m.paypal.com" if MODE == "live" else "https://api-m.sandbox.paypal.com"

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: PAYPAL_CLIENT_ID o PAYPAL_CLIENT_SECRET no configurados en .env")
    sys.exit(1)

PRODUCTS = [
    {
        "key":         "starter",
        "name":        "Nich-Ká Starter",
        "description": "1 kit activo, hasta 5 docentes, estudiantes ilimitados, NLP básico",
        "monthly_usd": "49.00",
        "annual_usd":  "490.00",
    },
    {
        "key":         "academic",
        "name":        "Nich-Ká Academic",
        "description": "Hasta 5 kits activos, docentes y estudiantes ilimitados, NLP avanzado",
        "monthly_usd": "129.00",
        "annual_usd":  "1290.00",
    },
    {
        "key":         "enterprise",
        "name":        "Nich-Ká Enterprise",
        "description": "Kits ilimitados, multi-admin, API access, white label, soporte dedicado",
        "monthly_usd": "299.00",
        "annual_usd":  "2990.00",
    },
]


async def get_token(client: httpx.AsyncClient) -> str:
    res = await client.post(
        f"{BASE_URL}/v1/oauth2/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
    )
    res.raise_for_status()
    return res.json()["access_token"]


async def create_product(client: httpx.AsyncClient, token: str, name: str, description: str) -> str:
    res = await client.post(
        f"{BASE_URL}/v1/catalogs/products",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "name":        name,
            "description": description,
            "type":        "SERVICE",
            "category":    "SOFTWARE",
        },
    )
    res.raise_for_status()
    return res.json()["id"]


async def create_plan(
    client:     httpx.AsyncClient,
    token:      str,
    product_id: str,
    name:       str,
    amount:     str,
    interval:   str,
) -> str:
    interval_unit  = "MONTH" if interval == "monthly" else "YEAR"
    interval_count = 1

    res = await client.post(
        f"{BASE_URL}/v1/billing/plans",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "product_id":   product_id,
            "name":         name,
            "status":       "ACTIVE",
            "billing_cycles": [
                {
                    "frequency":       {"interval_unit": interval_unit, "interval_count": interval_count},
                    "tenure_type":     "REGULAR",
                    "sequence":        1,
                    "total_cycles":    0,
                    "pricing_scheme":  {"fixed_price": {"value": amount, "currency_code": "USD"}},
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding":     True,
                "setup_fee_failure_action":  "CONTINUE",
                "payment_failure_threshold": 3,
            },
        },
    )
    res.raise_for_status()
    return res.json()["id"]


async def main() -> None:
    plan_ids: dict[str, str] = {}

    async with httpx.AsyncClient() as client:
        token = await get_token(client)
        print(f"Token obtenido ({MODE} mode)\n")

        for product in PRODUCTS:
            print(f"Creando producto: {product['name']} ...")
            product_id = await create_product(client, token, product["name"], product["description"])
            print(f"  product_id: {product_id}")

            monthly_id = await create_plan(
                client, token, product_id,
                f"{product['name']} — Mensual",
                product["monthly_usd"],
                "monthly",
            )
            annual_id = await create_plan(
                client, token, product_id,
                f"{product['name']} — Anual",
                product["annual_usd"],
                "annual",
            )

            key = product["key"].upper()
            plan_ids[f"PAYPAL_PLAN_{key}_MONTHLY"] = monthly_id
            plan_ids[f"PAYPAL_PLAN_{key}_ANNUAL"]  = annual_id

            print(f"  monthly plan: {monthly_id}")
            print(f"  annual  plan: {annual_id}")

    print("\n\n── Agrega estas líneas a tu .env ─────────────────────────")
    for key, value in plan_ids.items():
        print(f"{key}={value}")
    print("──────────────────────────────────────────────────────────")


asyncio.run(main())
