from src.core.rabbitmq.ws_events import to_room


async def receive_ml_result(result: dict) -> None:
    circuit_id = result["circuit_id"]
    await to_room("notifications", f"circuit:{circuit_id}", result)