from src.services.support.domain.dto.admin_schema import AdminResponse
from src.services.support.domain.repository.support_repository import SupportRepository


class GetAdminsUseCase:
    def __init__(self, repository: SupportRepository):
        self.repository = repository

    async def execute(self) -> list[AdminResponse]:
        admins = await self.repository.get_admins()
        return [AdminResponse.from_entity(admin) for admin in admins]
