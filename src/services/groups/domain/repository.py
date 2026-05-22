from abc import ABC, abstractmethod

from src.services.groups.domain.entities.group import Group


class IGroupRepository(ABC):

    @abstractmethod
    async def create(self, name: str, professor_id: int, code: str) -> Group:
        ...

    @abstractmethod
    async def get_all_by_professor(self, professor_id: int) -> list[Group]:
        ...

    @abstractmethod
    async def get_by_id(self, group_id: int) -> Group | None:
        ...

    @abstractmethod
    async def delete(self, group_id: int) -> None:
        ...

    @abstractmethod
    async def add_member(self, group_id: int, student_id: int) -> Group:
        ...

    @abstractmethod
    async def remove_member(self, group_id: int, student_id: int) -> None:
        ...

    @abstractmethod
    async def student_has_group(self, student_id: int) -> bool:
        ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Group | None:
        ...
