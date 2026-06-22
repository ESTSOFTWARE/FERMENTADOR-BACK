from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, select, text, update
from sqlalchemy.orm import relationship, selectinload

from src.core.database import Base
from src.services.fermentadores.domain.entities.fermentador import Fermentador
from src.services.fermentadores.domain.repository import IFermentadorRepository


# ── Modelo ORM ────────────────────────────────────────────────────────────────
class FermentadorModel(Base):
    __tablename__  = "fermentadores"
    __table_args__ = {"extend_existing": True}

    id         = Column(Integer, primary_key=True, autoincrement=True)
    serial     = Column(String(20), nullable=False, unique=True)
    circuit_id = Column(Integer, ForeignKey("circuits.id", ondelete="SET NULL"), nullable=True)
    vendido    = Column(Boolean, nullable=False, server_default=text("false"))
    estado     = Column(String(20), nullable=False, server_default=text("'disponible'"))
    cliente_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    circuit = relationship("CircuitModel", foreign_keys=[circuit_id], viewonly=True)
    creator = relationship("UserModel",    foreign_keys=[created_by], viewonly=True)
    cliente = relationship("UserModel",    foreign_keys=[cliente_id], viewonly=True)


def _full_name(user) -> str | None:
    if not user:
        return None
    return f"{user.name} {user.last_name}".strip()


class FermentadorRepository(IFermentadorRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _to_entity(self, model: FermentadorModel) -> Fermentador:
        return Fermentador(
            id             = model.id,
            serial         = model.serial,
            circuit_id     = model.circuit_id,
            vendido        = model.vendido,
            estado         = model.estado,
            created_by     = model.created_by,
            cliente_id     = model.cliente_id,
            created_at     = model.created_at,
            codigo         = model.circuit.activation_code if model.circuit else None,
            alta_por       = _full_name(model.creator),
            cliente_nombre = _full_name(model.cliente),
        )

    @staticmethod
    def _with_relations(stmt):
        return stmt.options(
            selectinload(FermentadorModel.circuit),
            selectinload(FermentadorModel.creator),
            selectinload(FermentadorModel.cliente),
        )

    async def create(self, serial: str, circuit_id: int, created_by: int | None) -> Fermentador:
        async with self._session_factory() as session:
            model = FermentadorModel(serial=serial, circuit_id=circuit_id, created_by=created_by)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            new_id = model.id
        # Re-leemos con relaciones para devolver código y nombres
        return await self.get_by_id(new_id)  # type: ignore[return-value]

    async def get_all(self) -> list[Fermentador]:
        async with self._session_factory() as session:
            result = await session.execute(
                self._with_relations(select(FermentadorModel)).order_by(FermentadorModel.id.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, fermentador_id: int) -> Fermentador | None:
        async with self._session_factory() as session:
            result = await session.execute(
                self._with_relations(select(FermentadorModel)).where(FermentadorModel.id == fermentador_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def serial_exists(self, serial: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentadorModel.id).where(FermentadorModel.serial == serial)
            )
            return result.scalar_one_or_none() is not None

    async def update(
        self,
        fermentador_id: int,
        vendido:    bool | None = None,
        estado:     str | None = None,
        cliente_id: int | None = None,
    ) -> Fermentador | None:
        values: dict = {}
        if vendido is not None:
            values["vendido"] = vendido
        if estado is not None:
            values["estado"] = estado
        if cliente_id is not None:
            values["cliente_id"] = cliente_id
        if values:
            async with self._session_factory() as session:
                await session.execute(
                    update(FermentadorModel).where(FermentadorModel.id == fermentador_id).values(**values)
                )
                await session.commit()
        return await self.get_by_id(fermentador_id)
