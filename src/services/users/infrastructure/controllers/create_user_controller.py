from src.core.database import AsyncSessionLocal
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.MySQL import (
    NotificationRepository,
)
from src.services.users.application.usecase.create_user_use_case import CreateUserUseCase
from src.services.users.domain.dto.create_user_schema import CreateUserRequest
from src.services.users.domain.dto.user_schema import UserResponse
from src.services.users.infrastructure.adapters.circuit_lookup_adapter import CircuitLookupAdapter
from src.services.users.infrastructure.adapters.MySQL import UserRepository

_ROLE_LABEL = {"profesor": "profesor", "estudiante": "alumno"}


async def create(body: CreateUserRequest, created_by: int, creator_role: str) -> UserResponse:
    repo         = UserRepository(AsyncSessionLocal)
    circuit_repo = CircuitLookupAdapter(AsyncSessionLocal)
    user = await CreateUserUseCase(repo, circuit_repo).execute(
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        password=body.password,
        role=body.role,
        created_by=created_by,
        creator_role=creator_role,
        activation_code=body.activation_code,
        dial_code=body.dial_code,
        phone_number=body.phone_number,
    )

    label = _ROLE_LABEL.get(body.role, body.role)
    notif_repo = NotificationRepository(AsyncSessionLocal)
    await SendNotificationUseCase(notif_repo).execute(
        user_id=created_by,
        message=f"{body.name} {body.last_name} fue registrado como {label}.",
        notification_type="user_registered",
    )

    return UserResponse.from_entity(user)
