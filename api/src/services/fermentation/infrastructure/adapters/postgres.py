import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    select,
    text,
    update,
)
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.services.fermentation.domain.entities.fermentation_report import FermentationReport
from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.entities.fermentation_status import FermentationStatus
from src.services.fermentation.domain.entities.report_history import ReportHistory
from src.services.fermentation.domain.repository import IFermentationRepository
from src.services.fermentation.infrastructure.mappers.sensor_mappings import (
    SENSOR_REPORT_MAP,
    SENSOR_TABLE_MAP,
)


class FermentationSessionModel(Base):
    __tablename__ = "fermentation_sessions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_id = Column(Integer, ForeignKey("circuits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True)
    formula_id = Column(Integer, ForeignKey(
        "efficiency_formula.id"), nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    status = Column(
        Enum("scheduled", "running", "completed", "interrupted", native_enum=False),
        nullable=False,
        default="scheduled",
    )
    interrupted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    circuit = relationship(
        "CircuitModel", back_populates="fermentation_sessions")
    report = relationship(
        "FermentationReportModel",
        back_populates="session",
        uselist=False,
    )


class FermentationReportModel(Base):
    __tablename__ = "fermentation_reports"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey(
        "fermentation_sessions.id"), nullable=False, unique=True)
    initial_sugar = Column(Float, nullable=False)
    final_sugar = Column(Float, nullable=True)
    ethanol_detected = Column(Float, nullable=True)
    theoretical_ethanol = Column(Float, nullable=True)
    efficiency = Column(Float, nullable=True)
    alcohol_initial = Column(Float, nullable=True)
    alcohol_final = Column(Float, nullable=True)
    alcohol_deactivated_at = Column(DateTime, nullable=True)
    alcohol_last_reading = Column(Float, nullable=True)
    density_initial = Column(Float, nullable=True)
    density_final = Column(Float, nullable=True)
    density_deactivated_at = Column(DateTime, nullable=True)
    density_last_reading = Column(Float, nullable=True)
    conductivity_initial = Column(Float, nullable=True)
    conductivity_final = Column(Float, nullable=True)
    conductivity_deactivated_at = Column(DateTime, nullable=True)
    conductivity_last_reading = Column(Float, nullable=True)
    ph_initial = Column(Float, nullable=True)
    ph_final = Column(Float, nullable=True)
    ph_deactivated_at = Column(DateTime, nullable=True)
    ph_last_reading = Column(Float, nullable=True)
    temperature_initial = Column(Float, nullable=True)
    temperature_final = Column(Float, nullable=True)
    temperature_deactivated_at = Column(DateTime, nullable=True)
    temperature_last_reading = Column(Float, nullable=True)
    turbidity_initial = Column(Float, nullable=True)
    turbidity_final = Column(Float, nullable=True)
    turbidity_deactivated_at = Column(DateTime, nullable=True)
    turbidity_last_reading = Column(Float, nullable=True)
    rpm_initial = Column(Float, nullable=True)
    rpm_final = Column(Float, nullable=True)
    rpm_deactivated_at = Column(DateTime, nullable=True)
    rpm_last_reading = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    generated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    session = relationship("FermentationSessionModel", back_populates="report")
    history = relationship("ReportHistoryModel", back_populates="report")


class ReportHistoryModel(Base):
    __tablename__ = "report_history"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey(
        "fermentation_reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(
        Enum("generated", "downloaded", "viewed", native_enum=False),
        nullable=False,
        default="generated",
    )
    occurred_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    report = relationship("FermentationReportModel", back_populates="history")


class EfficiencyFormulaModel(Base):
    __tablename__ = "efficiency_formula"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    conversion_factor = Column(Float, nullable=False, default=0.51)
    is_active = Column(Integer, nullable=False, default=1)


# ── Repositorio ───────────────────────────────────────────────────────────────
class FermentationRepository(IFermentationRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def create_session(
        self,
        circuit_id:      int,
        user_id:         int,
        formula_id:      int,
        scheduled_start: datetime,
        scheduled_end:   datetime,
        group_id:        int | None = None,
    ) -> FermentationSession:
        async with self._session_factory() as session:
            model = FermentationSessionModel(
                circuit_id=circuit_id,
                user_id=user_id,
                group_id=group_id,
                formula_id=formula_id,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                status="scheduled",
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._session_to_entity(model)

    async def get_session_by_id(self, session_id: int) -> FermentationSession | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentationSessionModel)
                .where(FermentationSessionModel.id == session_id)
            )
            model = result.scalar_one_or_none()
            return self._session_to_entity(model) if model else None

    async def get_sessions_by_user(self, user_id: int) -> list[FermentationSession]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentationSessionModel)
                .where(FermentationSessionModel.user_id == user_id)
                .order_by(FermentationSessionModel.id.desc())
            )
        return [
            self._session_to_entity(m)
            for m in result.scalars().all()
        ]

    async def get_active_session_by_circuit(self, circuit_id: int) -> FermentationSession | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentationSessionModel)
                .where(
                    FermentationSessionModel.circuit_id == circuit_id,
                    FermentationSessionModel.status == "running",
                )
            )
            model = result.scalar_one_or_none()
            return self._session_to_entity(model) if model else None

    async def update_session_status(
        self,
        session_id:     int,
        status:         str,
        actual_start:   datetime | None = None,
        actual_end:     datetime | None = None,
        interrupted_by: int | None = None,
    ) -> FermentationSession:
        values = {"status": status}
        if actual_start:
            values["actual_start"] = actual_start
        if actual_end:
            values["actual_end"] = actual_end
        if interrupted_by:
            values["interrupted_by"] = interrupted_by

        async with self._session_factory() as session:
            await session.execute(
                update(FermentationSessionModel)
                .where(FermentationSessionModel.id == session_id)
                .values(**values)
            )
            await session.commit()
        return await self.get_session_by_id(session_id)

    async def create_report(self, session_id: int, initial_sugar: float) -> FermentationReport:
        async with self._session_factory() as session:
            model = FermentationReportModel(
                session_id=session_id,
                initial_sugar=initial_sugar,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._report_to_entity(model)

    async def get_report_by_session(self, session_id: int) -> FermentationReport | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentationReportModel)
                .where(FermentationReportModel.session_id == session_id)
            )
            model = result.scalar_one_or_none()
            return self._report_to_entity(model) if model else None

    async def update_report(self, report: FermentationReport) -> FermentationReport:
        async with self._session_factory() as session:
            await session.execute(
                update(FermentationReportModel)
                .where(FermentationReportModel.session_id == report.session_id)
                .values(
                    final_sugar=report.final_sugar,
                    ethanol_detected=report.ethanol_detected,
                    theoretical_ethanol=report.theoretical_ethanol,
                    efficiency=report.efficiency,
                    notes=report.notes,
                )
            )
            await session.commit()
        return await self.get_report_by_session(report.session_id)

    async def update_sensor_deactivation(
        self,
        session_id:     int,
        sensor_type:    str,
        last_reading:   float,
        deactivated_at: datetime,
    ) -> None:
        cols = SENSOR_REPORT_MAP.get(sensor_type)
        if not cols:
            return
        _, _, col_deactivated, col_last = cols

        async with self._session_factory() as session:
            await session.execute(
                update(FermentationReportModel)
                .where(FermentationReportModel.session_id == session_id)
                .values({col_deactivated: deactivated_at, col_last: last_reading})
            )
            await session.commit()

    async def update_sensor_initial(self, session_id: int, sensor_type: str, value: float) -> None:
        cols = SENSOR_REPORT_MAP.get(sensor_type)
        if not cols:
            return
        col_initial = cols[0]

        async with self._session_factory() as session:
            await session.execute(
                update(FermentationReportModel)
                .where(FermentationReportModel.session_id == session_id)
                .values({col_initial: value})
            )
            await session.commit()

    async def update_sensor_final(self, session_id: int, sensor_type: str, value: float) -> None:
        cols = SENSOR_REPORT_MAP.get(sensor_type)
        if not cols:
            return
        col_final = cols[1]

        async with self._session_factory() as session:
            await session.execute(
                update(FermentationReportModel)
                .where(FermentationReportModel.session_id == session_id)
                .values({col_final: value})
            )
            await session.commit()

    async def create_report_history(self, report_id: int, user_id: int, action: str) -> ReportHistory:
        async with self._session_factory() as session:
            model = ReportHistoryModel(
                report_id=report_id,
                user_id=user_id,
                action=action,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return ReportHistory(
                id=model.id,
                report_id=model.report_id,
                user_id=model.user_id,
                action=model.action,
                occurred_at=model.occurred_at,
            )

    async def get_report_history_by_user(self, user_id: int) -> list[ReportHistory]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReportHistoryModel)
                .where(ReportHistoryModel.user_id == user_id)
                .order_by(ReportHistoryModel.occurred_at.desc())
            )
            return [
                ReportHistory(
                    id=m.id,
                    report_id=m.report_id,
                    user_id=m.user_id,
                    action=m.action,
                    occurred_at=m.occurred_at,
                )
                for m in result.scalars().all()
            ]

    async def get_user_id_by_circuit(self, circuit_id: int) -> int | None:
        """
        Retorna el user_id del dueño de la sesión activa en el circuito.
        Buscamos en fermentation_sessions en lugar de users para evitar
        acoplamiento con el servicio de auth.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentationSessionModel.user_id)
                .where(
                    FermentationSessionModel.circuit_id == circuit_id,
                    FermentationSessionModel.status == "running",
                )
                .order_by(FermentationSessionModel.id.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

    async def get_active_sensors_for_circuit(self, circuit_id: int) -> list[str]:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT sensor_alcohol_on, sensor_density_on, sensor_conductivity_on,"
                    " sensor_ph_on, sensor_temperature_on, sensor_turbidity_on, sensor_rpm_on"
                    " FROM circuits WHERE id = :id"
                ),
                {"id": circuit_id},
            )
            row = result.fetchone()
            if not row:
                return []
            keys = ["alcohol", "density", "conductivity", "ph", "temperature", "turbidity", "rpm"]
            return [k for k, v in zip(keys, row) if v]

    async def get_latest_sensor_reading(self, circuit_id: int, sensor_type: str) -> float | None:
        entry = SENSOR_TABLE_MAP.get(sensor_type)
        if not entry:
            return None
        table, col = entry
        async with self._session_factory() as session:
            result = await session.execute(
                text(f"SELECT {col} FROM {table} WHERE circuit_id = :cid ORDER BY timestamp DESC LIMIT 1"),
                {"cid": circuit_id},
            )
            row = result.fetchone()
            return float(row[0]) if row else None

    async def get_active_formula_factor(self) -> float:
        async with self._session_factory() as session:
            result = await session.execute(
                select(EfficiencyFormulaModel.conversion_factor)
                .where(EfficiencyFormulaModel.is_active == 1)
                .limit(1)
            )
            factor = result.scalar_one_or_none()
            return factor if factor is not None else 0.51

    # ── Mappers ───────────────────────────────────────────────────────────────
    def _session_to_entity(self, model: FermentationSessionModel) -> FermentationSession:
        return FermentationSession(
            id=model.id,
            circuit_id=model.circuit_id,
            user_id=model.user_id,
            group_id=model.group_id,
            formula_id=model.formula_id,
            scheduled_start=model.scheduled_start,
            scheduled_end=model.scheduled_end,
            status=FermentationStatus(model.status),
            actual_start=model.actual_start,
            actual_end=model.actual_end,
            interrupted_by=model.interrupted_by,
            created_at=model.created_at,
        )

    def _report_to_entity(self, model: FermentationReportModel) -> FermentationReport:
        return FermentationReport(
            id=model.id,
            session_id=model.session_id,
            initial_sugar=model.initial_sugar,
            final_sugar=model.final_sugar,
            ethanol_detected=model.ethanol_detected,
            theoretical_ethanol=model.theoretical_ethanol,
            efficiency=model.efficiency,
            alcohol_initial=model.alcohol_initial,
            alcohol_final=model.alcohol_final,
            alcohol_deactivated_at=model.alcohol_deactivated_at,
            alcohol_last_reading=model.alcohol_last_reading,
            density_initial=model.density_initial,
            density_final=model.density_final,
            density_deactivated_at=model.density_deactivated_at,
            density_last_reading=model.density_last_reading,
            conductivity_initial=model.conductivity_initial,
            conductivity_final=model.conductivity_final,
            conductivity_deactivated_at=model.conductivity_deactivated_at,
            conductivity_last_reading=model.conductivity_last_reading,
            ph_initial=model.ph_initial,
            ph_final=model.ph_final,
            ph_deactivated_at=model.ph_deactivated_at,
            ph_last_reading=model.ph_last_reading,
            temperature_initial=model.temperature_initial,
            temperature_final=model.temperature_final,
            temperature_deactivated_at=model.temperature_deactivated_at,
            temperature_last_reading=model.temperature_last_reading,
            turbidity_initial=model.turbidity_initial,
            turbidity_final=model.turbidity_final,
            turbidity_deactivated_at=model.turbidity_deactivated_at,
            turbidity_last_reading=model.turbidity_last_reading,
            rpm_initial=model.rpm_initial,
            rpm_final=model.rpm_final,
            rpm_deactivated_at=model.rpm_deactivated_at,
            rpm_last_reading=model.rpm_last_reading,
            notes=model.notes,
            generated_at=model.generated_at,
        )

    async def get_active_by_user(self, user_id: int):
        async with self._session_factory() as session:
            result = await session.execute(
                select(FermentationSessionModel)
                .where(
                    FermentationSessionModel.user_id == user_id,
                    FermentationSessionModel.status == 'running',
                )
                .order_by(FermentationSessionModel.id.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()
            return self._session_to_entity(model) if model else None
