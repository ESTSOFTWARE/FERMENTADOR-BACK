import asyncio
import logging
import threading
from abc import ABC, abstractmethod
from datetime import datetime

from src.core.config import settings

logger = logging.getLogger(__name__)


class BaseSensorThread(ABC):
    """
    Clase base para los hilos de cada sensor.

    Cada sensor activo durante una fermentación tendrá su propio hilo
    corriendo independientemente. El hilo vive desde que inicia la
    fermentación hasta que termina o el sensor se desactiva.

    Responsabilidad del hilo:
    - Mantener su propio event loop async
    - Escuchar su queue específica en RabbitMQ
    - Persistir cada lectura en DB
    - Hacer broadcast al front vía websocket_manager
    """

    def __init__(
        self,
        circuit_id: int,
        session_id: int,
        sensor_type: str,
    ):
        self.circuit_id  = circuit_id
        self.session_id  = session_id
        self.sensor_type = sensor_type

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._loop:   asyncio.AbstractEventLoop | None = None

    # ── Ciclo de vida ─────────────────────────────────────────────────────────
    def start(self) -> None:
        """
        Arranca el hilo. Crea un event loop propio para correr
        las corrutinas async de forma independiente al loop principal.
        """
        if self._thread and self._thread.is_alive():
            logger.warning(
                f"[Thread] Ya existe un hilo activo → "
                f"sensor={self.sensor_type} | circuit={self.circuit_id}"
            )
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=f"sensor_{self.sensor_type}_{self.circuit_id}",
            daemon=True,    # El hilo muere automáticamente si la app principal muere
        )
        self._thread.start()
        logger.info(
            f"[Thread] Hilo iniciado → "
            f"sensor={self.sensor_type} | circuit={self.circuit_id}"
        )

    def stop(self) -> None:
        """
        Detiene el hilo de forma ordenada.
        Señaliza el stop_event y espera a que el hilo termine.
        """
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                logger.warning(
                    f"[Thread] El hilo no terminó en 10s → "
                    f"sensor={self.sensor_type} | circuit={self.circuit_id}"
                )
            else:
                logger.info(
                    f"[Thread] Hilo detenido correctamente → "
                    f"sensor={self.sensor_type} | circuit={self.circuit_id}"
                )

        self._thread = None
        self._loop   = None

    def is_running(self) -> bool:
        """Verifica si el hilo está activo."""
        return self._thread is not None and self._thread.is_alive()

    # ── Event loop propio ─────────────────────────────────────────────────────
    def _run(self) -> None:
        """
        Entry point del hilo. Crea un event loop propio y
        corre la corrutina principal hasta que se detenga.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._main_loop())
        except Exception as e:
            logger.error(
                f"[Thread] Error en el hilo → "
                f"sensor={self.sensor_type} | circuit={self.circuit_id} | error={e}"
            )
        finally:
            self._loop.close()
            logger.info(
                f"[Thread] Event loop cerrado → "
                f"sensor={self.sensor_type} | circuit={self.circuit_id}"
            )

    async def _main_loop(self) -> None:
        """
        Loop principal del hilo. Corre hasta que se llame a stop().
        Delega el procesamiento de cada lectura a process_reading().
        """
        logger.info(
            f"[Thread] Loop iniciado → "
            f"sensor={self.sensor_type} | circuit={self.circuit_id}"
        )

        while not self._stop_event.is_set():
            try:
                await self.process_reading()
            except Exception as e:
                logger.error(
                    f"[Thread] Error en process_reading → "
                    f"sensor={self.sensor_type} | error={e}"
                )
                # Espera un segundo antes de reintentar para no saturar logs
                await asyncio.sleep(1)

        logger.info(
            f"[Thread] Loop finalizado → "
            f"sensor={self.sensor_type} | circuit={self.circuit_id}"
        )

    # ── Método abstracto ──────────────────────────────────────────────────────
    @abstractmethod
    async def process_reading(self) -> None:
        """
        Cada sensor concreto implementa su lógica aquí.

        Responsabilidades típicas:
        - Esperar una lectura de su queue en RabbitMQ
        - Persistir la lectura en DB
        - Hacer broadcast al front vía ws_manager

        Este método se llama en loop hasta que stop() sea invocado.
        """
        ...

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _should_stop(self) -> bool:
        """Verifica si el hilo debe detenerse."""
        return self._stop_event.is_set()

    def _log(self, level: str, message: str) -> None:
        """Logger con contexto del sensor."""
        prefix = (
            f"[Thread:{self.sensor_type}:{self.circuit_id}] {message}"
        )
        getattr(logger, level)(prefix)