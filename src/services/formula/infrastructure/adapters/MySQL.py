from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
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
from src.core.exceptions import FormulaNotFoundException
from src.services.formula.domain.entities.efficiency_formula import EfficiencyFormula
from src.services.formula.domain.repository import IFormulaRepository


# ── Modelo ORM ────────────────────────────────────────────────────────────────
class EfficiencyFormulaModel(Base):
    __tablename__  = "efficiency_formula"
    __table_args__ = {"extend_existing": True}

    id                = Column(Integer, primary_key=True, autoincrement=True)
    name              = Column(String(100), nullable=False)
    conversion_factor = Column(Float, nullable=False, default=0.51)
    description       = Column(Text, nullable=True)
    is_active         = Column(Boolean, nullable=False, default=True)
    updated_by        = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at        = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )
    created_at        = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updater = relationship("UserModel", foreign_keys=[updated_by])


# ── Repositorio ───────────────────────────────────────────────────────────────
class FormulaRepository(IFormulaRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_active(self) -> EfficiencyFormula | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(EfficiencyFormulaModel)
                .where(EfficiencyFormulaModel.is_active == True)  # noqa: E712
                .limit(1)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_id(self, formula_id: int) -> EfficiencyFormula | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(EfficiencyFormulaModel)
                .where(EfficiencyFormulaModel.id == formula_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_all(self) -> list[EfficiencyFormula]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(EfficiencyFormulaModel)
                .order_by(EfficiencyFormulaModel.id)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def update(
        self,
        formula_id:        int,
        name:              str | None,
        conversion_factor: float | None,
        description:       str | None,
        updated_by:        int,
    ) -> EfficiencyFormula:
        values = {"updated_by": updated_by}
        if name is not None:
            values["name"] = name
        if conversion_factor is not None:
            values["conversion_factor"] = conversion_factor
        if description is not None:
            values["description"] = description

        async with self._session_factory() as session:
            await session.execute(
                update(EfficiencyFormulaModel)
                .where(EfficiencyFormulaModel.id == formula_id)
                .values(**values)
            )
            await session.commit()

        formula = await self.get_by_id(formula_id)
        if not formula:
            raise FormulaNotFoundException()
        return formula

    async def set_active(self, formula_id: int) -> EfficiencyFormula:
        async with self._session_factory() as session:
            await session.execute(
                update(EfficiencyFormulaModel).values(is_active=False)
            )
            await session.execute(
                update(EfficiencyFormulaModel)
                .where(EfficiencyFormulaModel.id == formula_id)
                .values(is_active=True)
            )
            await session.commit()

        formula = await self.get_by_id(formula_id)
        if not formula:
            raise FormulaNotFoundException()
        return formula

    def _to_entity(self, model: EfficiencyFormulaModel) -> EfficiencyFormula:
        return EfficiencyFormula(
            id=model.id,
            name=model.name,
            conversion_factor=model.conversion_factor,
            description=model.description,
            is_active=model.is_active,
            updated_by=model.updated_by,
            updated_at=model.updated_at,
            created_at=model.created_at,
        )