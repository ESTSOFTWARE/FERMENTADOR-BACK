from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App 
    APP_NAME: str = "sensor_db_backend"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # JWT 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_SSL: bool = False   # True para BD gestionada con SSL (ej. Supabase en prod)

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str = ""  # CloudAMQP exige el vhost (= usuario); local usa "" (default)

    @property
    def RABBITMQ_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"
        )

    # OAuth — Google 
    GOOGLE_CLIENT_ID:     str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI:  str = "http://localhost:8000/api/auth/callback/google"

    # OAuth — GitHub
    GITHUB_CLIENT_ID:     str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI:  str = "http://localhost:8000/api/auth/callback/github"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Cookies
    COOKIE_SECURE:   bool = False   # True en producción (HTTPS)
    COOKIE_SAMESITE: str  = "lax"
    COOKIE_DOMAIN:   str  = ""      # vacío = sin dominio explícito

    # PayPal
    PAYPAL_CLIENT_ID:     str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_MODE:          str = "sandbox"   # sandbox | live

    # PayPal Plan IDs (ejecutar scripts/setup_paypal_plans.py para generarlos)
    PAYPAL_PLAN_STARTER_MONTHLY:    str = ""
    PAYPAL_PLAN_STARTER_ANNUAL:     str = ""
    PAYPAL_PLAN_ACADEMIC_MONTHLY:   str = ""
    PAYPAL_PLAN_ACADEMIC_ANNUAL:    str = ""
    PAYPAL_PLAN_ENTERPRISE_MONTHLY: str = ""
    PAYPAL_PLAN_ENTERPRISE_ANNUAL:  str = ""

    # Stripe
    STRIPE_SECRET_KEY:    str = ""
    STRIPE_PUBLIC_KEY:    str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Stripe Price IDs (ejecutar scripts/setup_stripe_products.py para generarlos)
    STRIPE_PRICE_STARTER_MONTHLY:    str = ""
    STRIPE_PRICE_STARTER_ANNUAL:     str = ""
    STRIPE_PRICE_ACADEMIC_MONTHLY:   str = ""
    STRIPE_PRICE_ACADEMIC_ANNUAL:    str = ""
    STRIPE_PRICE_ENTERPRISE_MONTHLY: str = ""
    STRIPE_PRICE_ENTERPRISE_ANNUAL:  str = ""

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY:    str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Resend (email) 
    RESEND_API_KEY:  str = ""
    MAIL_FROM:       str = ""
    MAIL_FROM_NAME:  str = "Nich-ká"

    # Sensores
    SENSOR_TYPES: list[str] = [
        "alcohol",
        "density",
        "conductivity",
        "ph",
        "temperature",
        "turbidity",
        "rpm",
    ]
    TEMPERATURE_ALERT_THRESHOLD: float = 40.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()