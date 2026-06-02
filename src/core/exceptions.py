from fastapi import HTTPException, status


# ── Base ─────────────────────────────────────────────────────────────────────
class AppException(HTTPException):
    """Excepción base del sistema. Todas las demás heredan de esta."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


# ── Auth ──────────────────────────────────────────────────────────────────────
class InvalidResetCodeException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificación inválido o expirado"
        )

class TooManyRequestsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes. Intenta de nuevo más tarde"
        )

class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado"
        )

class TokenInvalidException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

class UnauthorizedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )

class ForbiddenException(AppException):
    def __init__(self, detail: str = "No tienes permisos para realizar esta acción"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class EmailAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="El email ya está registrado")


# ── Usuarios ──────────────────────────────────────────────────────────────────
class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

class AccountDeactivatedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está desactivada. Inicia sesión con OAuth para reactivarla."
        )

class UserAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email"
        )


# ── Circuitos ─────────────────────────────────────────────────────────────────
class CircuitNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Circuito no encontrado"
        )

class CircuitAlreadyActivatedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este código de activación ya fue utilizado"
        )

class CircuitNotActivatedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El circuito no está activado"
        )

class InvalidActivationCodeException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de activación inválido o no existe"
        )

class ActivationCodeExpiredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de activación ha expirado (30 días sin usar)"
        )


# ── Fermentación ──────────────────────────────────────────────────────────────
class FermentationSessionNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de fermentación no encontrada"
        )

class FermentationAlreadyRunningException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya hay una fermentación en curso para este circuito"
        )

class FermentationNotRunningException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay una fermentación en curso para este circuito"
        )

class FermentationReportNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte de fermentación no encontrado"
        )


# ── Sensores ──────────────────────────────────────────────────────────────────
class SensorNotFoundException(AppException):
    def __init__(self, sensor_type: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor '{sensor_type}' no encontrado"
        )

class SensorDisabledException(AppException):
    def __init__(self, sensor_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El sensor '{sensor_type}' está desactivado"
        )


# ── Fórmula ───────────────────────────────────────────────────────────────────
class FormulaNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fórmula de eficiencia no encontrada"
        )


# ── Productos ─────────────────────────────────────────────────────────────────
class ProductNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

class ProductAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese SKU"
        )


# ── RabbitMQ ──────────────────────────────────────────────────────────────────
class BrokerConnectionException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar al broker de mensajería"
        )

class MessagePublishException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al publicar mensaje en el broker"
        )


# ── Genéricas ─────────────────────────────────────────────────────────────────
class NotFoundException(AppException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ConflictException(AppException):
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

class BadRequestException(AppException):
    def __init__(self, detail: str = "Solicitud inválida"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class InvalidFileException(AppException):
    def __init__(self, detail: str = "Archivo inválido"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )