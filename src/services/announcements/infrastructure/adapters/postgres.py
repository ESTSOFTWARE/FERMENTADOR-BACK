from datetime import datetime, timedelta

from sqlalchemy import case, delete, select, update

from src.core.models.announcement_model import AnnouncementModel
from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.domain.repository import IAnnouncementRepository


class AnnouncementRepository(IAnnouncementRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_all(self) -> list[Announcement]:
        async with self._session_factory() as session:
            now = datetime.utcnow()
            pinned_first = case(
                (
                    AnnouncementModel.is_pinned &
                    (
                        AnnouncementModel.pinned_until.is_(None) |
                        (AnnouncementModel.pinned_until > now)
                    ),
                    0,
                ),
                else_=1,
            )
            result = await session.execute(
                select(AnnouncementModel).order_by(pinned_first, AnnouncementModel.created_at.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def create(
        self,
        label:       str,
        version:     str,
        date:        str,
        title:       str,
        description: str,
    ) -> Announcement:
        async with self._session_factory() as session:
            model = AnnouncementModel(
                label=label,
                version=version,
                date=date,
                title=title,
                description=description,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, announcement_id: int) -> Announcement | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(AnnouncementModel).where(AnnouncementModel.id == announcement_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def update(
        self,
        announcement_id: int,
        label:           str,
        version:         str,
        date:            str,
        title:           str,
        description:     str,
    ) -> Announcement:
        async with self._session_factory() as session:
            await session.execute(
                update(AnnouncementModel)
                .where(AnnouncementModel.id == announcement_id)
                .values(
                    label=label,
                    version=version,
                    date=date,
                    title=title,
                    description=description,
                )
            )
            await session.commit()
        return await self.get_by_id(announcement_id)

    async def delete(self, announcement_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(AnnouncementModel).where(AnnouncementModel.id == announcement_id)
            )
            await session.commit()

    async def pin(self, announcement_id: int, duration_days: int | None) -> Announcement:
        pinned_until = (
            datetime.utcnow() + timedelta(days=duration_days)
            if duration_days is not None
            else None
        )
        async with self._session_factory() as session:
            await session.execute(
                update(AnnouncementModel)
                .where(AnnouncementModel.id == announcement_id)
                .values(is_pinned=True, pinned_until=pinned_until)
            )
            await session.commit()
        return await self.get_by_id(announcement_id)

    async def unpin(self, announcement_id: int) -> Announcement:
        async with self._session_factory() as session:
            await session.execute(
                update(AnnouncementModel)
                .where(AnnouncementModel.id == announcement_id)
                .values(is_pinned=False, pinned_until=None)
            )
            await session.commit()
        return await self.get_by_id(announcement_id)

    def _to_entity(self, model: AnnouncementModel) -> Announcement:
        return Announcement(
            id=model.id,
            label=model.label,
            version=model.version,
            date=model.date,
            title=model.title,
            description=model.description,
            created_at=model.created_at,
            is_pinned=model.is_pinned or False,
            pinned_until=model.pinned_until,
        )
