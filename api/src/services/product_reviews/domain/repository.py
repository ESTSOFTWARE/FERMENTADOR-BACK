from abc import ABC, abstractmethod

from src.services.product_reviews.domain.entities.review import Review


class IReviewRepository(ABC):

    @abstractmethod
    async def get_by_product(self, product_id: int, page: int, limit: int) -> list[Review]:
        ...

    @abstractmethod
    async def get_by_id(self, review_id: int) -> Review | None:
        ...

    @abstractmethod
    async def get_by_user_and_product(self, user_id: int, product_id: int) -> Review | None:
        ...

    @abstractmethod
    async def count_by_product(self, product_id: int) -> int:
        ...

    @abstractmethod
    async def average_rating_by_product(self, product_id: int) -> float:
        ...

    @abstractmethod
    async def create(self, review: Review) -> Review:
        ...

    @abstractmethod
    async def delete(self, review_id: int) -> None:
        ...