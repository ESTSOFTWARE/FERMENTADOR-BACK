from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

# ── Motor async ──────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,      # Imprime SQL en consola solo en desarrollo
    pool_size=20,             # Conexiones base por worker (4 workers × 20 = 80 conexiones)
    max_overflow=40,          # Picos: hasta 60 conexiones por worker si es necesario
    pool_pre_ping=True,       # Verifica que la conexión siga viva antes de usarla
    pool_recycle=1800,        # Recicla conexiones cada 30 min (MySQL cierra idle a los 8h)
    pool_timeout=30,          # Tiempo máximo esperando una conexión libre del pool
)

# ── Fábrica de sesiones ───────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # Los objetos siguen accesibles después del commit
    autocommit=False,
    autoflush=False,
)

# ── Base para todos los modelos SQLAlchemy ────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependencia de sesión para FastAPI ───────────────────────────────────────
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


# ── Inicializar tablas (solo desarrollo) ─────────────────────────────────────
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)