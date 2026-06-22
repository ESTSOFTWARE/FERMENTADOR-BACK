import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

# SSL para BD gestionada (Supabase, etc.)
# asyncpg recibe el contexto vía connect_args["ssl"]. Sin verificación de cert
# (el proveedor ya termina TLS) para evitar fallos por CA en el contenedor.
_connect_args = {}
if settings.DB_SSL:
    _ssl_ctx = ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE
    _connect_args["ssl"] = _ssl_ctx

# Motor async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,      # Imprime SQL en consola solo en desarrollo
    pool_size=settings.DB_POOL_SIZE,        # Conexiones base (chico para Supabase free)
    max_overflow=settings.DB_MAX_OVERFLOW,  # Conexiones extra en picos
    pool_pre_ping=True,       # Verifica que la conexión siga viva antes de usarla
    pool_recycle=1800,        # Recicla conexiones cada 30 min para evitar conexiones obsoletas
    pool_timeout=30,          # Tiempo máximo esperando una conexión libre del pool
    connect_args=_connect_args,
)

# Fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # Los objetos siguen accesibles después del commit
    autocommit=False,
    autoflush=False,
)

# Base para todos los modelos SQLAlchemy
class Base(DeclarativeBase):
    pass


# Dependencia de sesión para FastAPI
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Inicializar tablas (solo desarrollo)
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)