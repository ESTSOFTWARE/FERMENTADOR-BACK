from src.core.rabbitmq.ws_events import to_room


class SendMlResultUseCase:
    """
    Recibe el resultado del microservicio de ML (anomalía o predicción de
    eficiencia) y lo transmite en tiempo real a todos los sockets unidos a
    la room del circuito -- mismo mecanismo que ya usan las lecturas de
    sensores, sin necesidad de resolver una lista de usuarios.
    """

    async def execute(self, result: dict) -> None:
        circuit_id = result["circuit_id"]
        await to_room("notifications", f"circuit:{circuit_id}", result)