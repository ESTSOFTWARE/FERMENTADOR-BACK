from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, select, text

from src.core.database import Base
from src.services.sensors.domain.entities.sensor_reading import SensorReading
from src.services.sensors.domain.repository import ISensorRepository


# ── Modelos ORM ───────────────────────────────────────────────────────────────
class AlcoholSensorModel(Base):
    __tablename__  = "alcohol_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id        = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id            = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id            = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp             = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    alcohol_concentration = Column(Float, nullable=False)


class DensitySensorModel(Base):
    __tablename__  = "density_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id     = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp      = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    density        = Column(Float, nullable=False)


class ConductivitySensorModel(Base):
    __tablename__  = "conductivity_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id     = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp      = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    conductivity   = Column(Float, nullable=False)


class PhSensorModel(Base):
    __tablename__  = "ph_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id     = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp      = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    ph_value       = Column(Float, nullable=False)


class TemperatureSensorModel(Base):
    __tablename__  = "temperature_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id     = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp      = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    temperature    = Column(Float, nullable=False)


class TurbiditySensorModel(Base):
    __tablename__  = "turbidity_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id     = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp      = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    turbidity      = Column(Float, nullable=False)


class MotorRpmSensorModel(Base):
    __tablename__  = "motor_rpm_sensor"
    __table_args__ = {"extend_existing": True}

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id     = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    timestamp      = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    rpm            = Column(Float, nullable=False)


# Mapa sensor_type → (Model, columna_valor)
SENSOR_MODEL_MAP: dict[str, tuple] = {
    "alcohol":      (AlcoholSensorModel,      "alcohol_concentration"),
    "density":      (DensitySensorModel,      "density"),
    "conductivity": (ConductivitySensorModel, "conductivity"),
    "ph":           (PhSensorModel,           "ph_value"),
    "temperature":  (TemperatureSensorModel,  "temperature"),
    "turbidity":    (TurbiditySensorModel,    "turbidity"),
    "rpm":          (MotorRpmSensorModel,     "rpm"),
}


# ── Repositorio ───────────────────────────────────────────────────────────────
class SensorRepository(ISensorRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def save_reading(
        self,
        circuit_id:  int,
        sensor_type: str,
        value:       float,
        session_id:  int | None = None,
    ) -> SensorReading:
        Model, value_col = SENSOR_MODEL_MAP[sensor_type]

        async with self._session_factory() as session:
            model = Model(
                circuit_id=circuit_id,
                session_id=session_id,
                **{value_col: value},
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model, sensor_type, value_col)

    async def get_history(
        self,
        circuit_id:  int,
        sensor_type: str,
        session_id:  int | None = None,
        from_dt:     datetime | None = None,
        to_dt:       datetime | None = None,
    ) -> list[SensorReading]:
        Model, value_col = SENSOR_MODEL_MAP[sensor_type]

        async with self._session_factory() as session:
            query = (
                select(Model)
                .where(Model.circuit_id == circuit_id)
                .order_by(Model.timestamp.asc())
            )
            if session_id:
                query = query.where(Model.session_id == session_id)
            if from_dt:
                query = query.where(Model.timestamp >= from_dt)
            if to_dt:
                query = query.where(Model.timestamp <= to_dt)

            result = await session.execute(query)
            return [
                self._to_entity(m, sensor_type, value_col)
                for m in result.scalars().all()
            ]

    async def get_latest_reading(
        self,
        circuit_id:  int,
        sensor_type: str,
    ) -> SensorReading | None:
        Model, value_col = SENSOR_MODEL_MAP[sensor_type]

        async with self._session_factory() as session:
            result = await session.execute(
                select(Model)
                .where(Model.circuit_id == circuit_id)
                .order_by(Model.timestamp.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model, sensor_type, value_col) if model else None

    def _to_entity(self, model, sensor_type: str, value_col: str) -> SensorReading:
        return SensorReading(
            id=model.measurement_id,
            circuit_id=model.circuit_id,
            sensor_type=sensor_type,
            value=getattr(model, value_col),
            session_id=model.session_id,
            timestamp=model.timestamp,
        )