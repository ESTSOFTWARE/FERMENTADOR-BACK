"""
Ejecutar una sola vez para crear los productos y precios en Stripe.
Copia los IDs generados en el .env

    python scripts/setup_stripe_products.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

if not stripe.api_key:
    print("ERROR: STRIPE_SECRET_KEY no configurado en .env")
    sys.exit(1)

PRODUCTS = [
    {
        "key":         "starter",
        "name":        "Nich-Ká Starter",
        "description": "1 kit activo, hasta 5 docentes, estudiantes ilimitados, NLP básico",
        "monthly":     4900,
        "annual":      49000,
    },
    {
        "key":         "academic",
        "name":        "Nich-Ká Academic",
        "description": "Hasta 5 kits activos, docentes y estudiantes ilimitados, NLP avanzado",
        "monthly":     12900,
        "annual":      129000,
    },
    {
        "key":         "enterprise",
        "name":        "Nich-Ká Enterprise",
        "description": "Kits ilimitados, multi-admin, API access, white label, soporte dedicado",
        "monthly":     29900,
        "annual":      299000,
    },
]

price_ids: dict[str, str] = {}

for product in PRODUCTS:
    print(f"\nCreando producto: {product['name']} ...")
    p = stripe.Product.create(
        name=product["name"],
        description=product["description"],
    )

    monthly = stripe.Price.create(
        product=p.id,
        unit_amount=product["monthly"],
        currency="usd",
        recurring={"interval": "month"},
        nickname=f"{product['key']}_monthly",
    )
    annual = stripe.Price.create(
        product=p.id,
        unit_amount=product["annual"],
        currency="usd",
        recurring={"interval": "year"},
        nickname=f"{product['key']}_annual",
    )

    price_ids[f"STRIPE_PRICE_{product['key'].upper()}_MONTHLY"] = monthly.id
    price_ids[f"STRIPE_PRICE_{product['key'].upper()}_ANNUAL"]  = annual.id

    print(f"  monthly: {monthly.id}")
    print(f"  annual:  {annual.id}")

print("\n\n── Agrega estas líneas a tu .env ─────────────────────────")
for key, value in price_ids.items():
    print(f"{key}={value}")
print("──────────────────────────────────────────────────────────")
