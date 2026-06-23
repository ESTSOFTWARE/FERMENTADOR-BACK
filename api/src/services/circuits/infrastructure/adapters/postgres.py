from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, delete, select, text, update
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.services.circuits.domain.entities.circuit import Circuit
from src.services.circuits.domain.repository import ICircuitRepository


# ── Modelo ORM ────────────────────────────────────────────────────────────────
class CircuitModel(Base):
    __tablename__  = "circuits"
    __table_args__ = {"extend_existing": True}

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    activation_code         = Column(String(64), nullable=False, unique=True)
    activated_at            = Column(DateTime, nullable=True)
    is_active               = Column(Boolean, nullable=False, default=False)
    motor_on                = Column(Boolean, nullable=False, default=False)
    pump_on                 = Column(Boolean, nullable=False, default=False)
    sensor_alcohol_on       = Column(Boolean, nullable=False, default=False)
    sensor_density_on       = Column(Boolean, nullable=False, default=False)
    sensor_conductivity_on  = Column(Boolean, nullable=False, default=False)
    sensor_ph_on            = Column(Boolean, nullable=False, default=False)
    sensor_temperature_on   = Column(Boolean, nullable=False, default=False)
    sensor_turbidity_on     = Column(Boolean, nullable=False, default=False)
    sensor_rpm_on           = Column(Boolean, nullable=False, default=False)
    created_at              = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    fermentation_sessions = relationship(
        "FermentationSessionModel",
        back_populates="circuit",
    )


SENSOR_COLUMN_MAP = {
    "alcohol":      "sensor_alcohol_on",
    "density":      "sensor_density_on",
    "conductivity": "sensor_conductivity_on",
    "ph":           "sensor_ph_on",
    "temperature":  "sensor_temperature_on",
    "turbidity":    "sensor_turbidity_on",
    "rpm":          "sensor_rpm_on",
}

DEVICE_COLUMN_MAP = {
    "motor": "motor_on",
    "pump":  "pump_on",
}


# ── Repositorio ───────────────────────────────────────────────────────────────
class CircuitRepository(ICircuitRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_id(self, circuit_id: int) -> Circuit | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CircuitModel).where(CircuitModel.id == circuit_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_activation_code(self, code: str) -> Circuit | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CircuitModel).where(CircuitModel.activation_code == code)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(self, activation_code: str) -> Circuit:
        async with self._session_factory() as session:
            model = CircuitModel(activation_code=activation_code)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def activate(self, circuit_id: int) -> Circuit:
        async with self._session_factory() as session:
            await session.execute(
                update(CircuitModel)
                .where(CircuitModel.id == circuit_id)
                .values(
                    is_active=True,
                    activated_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
            await session.commit()
        return await self.get_by_id(circuit_id)

    async def update_sensor_state(
        self,
        circuit_id:  int,
        sensor_type: str,
        state:       bool,
    ) -> Circuit:
        column = SENSOR_COLUMN_MAP.get(sensor_type)
        if not column:
            raise ValueError(f"Sensor type desconocido: {sensor_type}")

        async with self._session_factory() as session:
            await session.execute(
                update(CircuitModel)
                .where(CircuitModel.id == circuit_id)
                .values({column: state})
            )
            await session.commit()
        return await self.get_by_id(circuit_id)

    async def update_device_state(
        self,
        circuit_id:  int,
        device_type: str,
        state:       bool,
    ) -> Circuit:
        column = DEVICE_COLUMN_MAP.get(device_type)
        if not column:
            raise ValueError(f"Device type desconocido: {device_type}")

        async with self._session_factory() as session:
            await session.execute(
                update(CircuitModel)
                .where(CircuitModel.id == circuit_id)
                .values({column: state})
            )
            await session.commit()
        return await self.get_by_id(circuit_id)

    async def delete_expired_unactivated(self, expiration_days: int) -> int:
        expiration_threshold = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=expiration_days)

        async with self._session_factory() as session:
            result = await session.execute(
                delete(CircuitModel)
                .where(
                    CircuitModel.is_active == False,  # noqa: E712
                    CircuitModel.created_at <= expiration_threshold,
                )
            )
            await session.commit()
            return result.rowcount

    def _to_entity(self, model: CircuitModel) -> Circuit:
        return Circuit(
            id=model.id,
            activation_code=model.activation_code,
            is_active=model.is_active,
            motor_on=model.motor_on,
            pump_on=model.pump_on,
            sensor_alcohol_on=model.sensor_alcohol_on,
            sensor_density_on=model.sensor_density_on,
            sensor_conductivity_on=model.sensor_conductivity_on,
            sensor_ph_on=model.sensor_ph_on,
            sensor_temperature_on=model.sensor_temperature_on,
            sensor_turbidity_on=model.sensor_turbidity_on,
            sensor_rpm_on=model.sensor_rpm_on,
            activated_at=model.activated_at,
            created_at=model.created_at,
        )