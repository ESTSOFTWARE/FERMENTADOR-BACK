from fastapi import HTTPException

from src.services.support.domain.dto.admin_schema import AdminResponse
from src.services.support.domain.repository.support_repository import SupportRepository


class GetAdminByIdUseCase:
    def __init__(self, repository: SupportRepository):
        self.repository = repository

    async def execute(self, admin_id: int) -> AdminResponse:
        admin = await self.repository.get_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return AdminResponse.from_entity(admin)
