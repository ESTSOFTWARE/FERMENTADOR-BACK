from abc import ABC, abstractmethod
from datetime import datetime

from src.services.fermentation.domain.entities.fermentation_report import FermentationReport
from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.entities.report_history import ReportHistory


class IFermentationRepository(ABC):

    @abstractmethod
    async def create_session(
        self,
        circuit_id:      int,
        user_id:         int,
        formula_id:      int,
        scheduled_start: datetime,
        scheduled_end:   datetime,
        group_id:        int | None = None,
    ) -> FermentationSession:
        ...
        
    @abstractmethod
    async def get_sessions_by_user(
        self, user_id: int
    ) -> list[FermentationSession]:
        ...

    @abstractmethod
    async def get_sessions_visible_to(
        self, user_id: int, role: str
    ) -> list[FermentationSession]:
        ...

    @abstractmethod
    async def get_session_by_id(
        self, session_id: int
    ) -> FermentationSession | None:
        ...

    @abstractmethod
    async def get_active_session_by_circuit(
        self, circuit_id: int
    ) -> FermentationSession | None:
        ...

    @abstractmethod
    async def get_running_sessions_past_end(
        self, now: datetime
    ) -> list[FermentationSession]:
        """Sesiones en estado 'running' cuyo scheduled_end ya pasó (para auto-detener)."""
        ...

    @abstractmethod
    async def update_session_status(
        self,
        session_id:     int,
        status:         str,
        actual_start:   datetime | None = None,
        actual_end:     datetime | None = None,
        interrupted_by: int | None = None,
    ) -> FermentationSession:
        ...

    @abstractmethod
    async def create_report(
        self,
        session_id:    int,
        initial_sugar: float,
    ) -> FermentationReport:
        ...

    @abstractmethod
    async def get_report_by_session(
        self, session_id: int
    ) -> FermentationReport | None:
        ...

    @abstractmethod
    async def update_report(
        self, report: FermentationReport
    ) -> FermentationReport:
        ...

    @abstractmethod
    async def update_sensor_deactivation(
        self,
        session_id:     int,
        sensor_type:    str,
        last_reading:   float,
        deactivated_at: datetime,
    ) -> None:
        ...

    @abstractmethod
    async def update_sensor_initial(
        self,
        session_id:  int,
        sensor_type: str,
        value:       float,
    ) -> None:
        ...

    @abstractmethod
    async def update_sensor_final(
        self,
        session_id:  int,
        sensor_type: str,
        value:       float,
    ) -> None:
        ...

    @abstractmethod
    async def create_report_history(
        self,
        report_id: int,
        user_id:   int,
        action:    str,
    ) -> ReportHistory:
        ...

    @abstractmethod
    async def get_report_history_by_user(
        self, user_id: int
    ) -> list[ReportHistory]:
        ...

    @abstractmethod
    async def get_user_id_by_circuit(
        self, circuit_id: int
    ) -> int | None:
        ...

    @abstractmethod
    async def get_active_formula_factor(self) -> float:
        ...

    @abstractmethod
    async def get_active_by_user(self, user_id: int):
        ...

    @abstractmethod
    async def get_active_sensors_for_circuit(self, circuit_id: int) -> list[str]:
        ...

    @abstractmethod
    async def get_latest_sensor_reading(self, circuit_id: int, sensor_type: str) -> float | None:
        ...