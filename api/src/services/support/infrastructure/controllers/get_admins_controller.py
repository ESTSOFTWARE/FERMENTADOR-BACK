from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_session
from src.services.support.application.usecase.get_admins_use_case import GetAdminsUseCase
from src.services.support.domain.dto.admin_schema import AdminResponse
from src.services.support.infrastructure.adapters.postgres import SupportRepositoryPostgres


async def get_admins_controller(
    session: AsyncSession = Depends(get_session),
) -> list[AdminResponse]:
    repository = SupportRepositoryPostgres(session)
    use_case = GetAdminsUseCase(repository)
    return await use_case.execute()
