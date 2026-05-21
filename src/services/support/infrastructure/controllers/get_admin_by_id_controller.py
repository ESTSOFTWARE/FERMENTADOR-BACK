from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_session
from src.services.support.application.usecase.get_admin_by_id_use_case import (
    GetAdminByIdUseCase,
)
from src.services.support.domain.dto.admin_schema import AdminResponse
from src.services.support.infrastructure.adapters.MySQL import SupportRepositoryMySQL


async def get_admin_by_id_controller(
    admin_id: int,
    session: AsyncSession = Depends(get_session),
) -> AdminResponse:
    repository = SupportRepositoryMySQL(session)
    use_case = GetAdminByIdUseCase(repository)
    return await use_case.execute(admin_id)
