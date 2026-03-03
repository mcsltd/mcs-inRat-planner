import asyncio
import logging
import copy
import queue
from asyncio import AbstractEventLoop
from threading import Lock, Thread

from PySide6.QtCore import QObject, Signal
from bleak import BLEDevice

from src.device.device import ECG_DataBlock
from src.device.inrat_v1.inrat import inRat

logger = logging.getLogger(__name__)

class inRatDevice(QObject):

    device_connected = Signal()
    device_started = Signal()
    device_stopped = Signal()
    device_disconnected = Signal()

    def __init__(self, loop: AbstractEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.inrat: inRat | None = None

        self._loop: AbstractEventLoop = loop
        self._receivers = []
        self._running = False
        # self._lock = Lock()
        self._input_queue = queue.Queue()
        self._async_queue = asyncio.Queue()



    def process_connect(self, ble_device: BLEDevice, wait=10):
        """ обработка соединение с устройством """
        if self.inrat and self.inrat.is_connected:
            logger.warning(f"{self.inrat.name} уже подсоединено!")
            return
        self.inrat = inRat(ble_device)
        future = asyncio.run_coroutine_threadsafe(self.inrat.connect(wait=wait), loop=self._loop)
        future.add_done_callback(self._on_device_connected)
    def _on_device_connected(self, future):
        """ обработка результата подключения к устройству """
        if future.result() and self.inrat.is_connected:
            logger.debug(f"{self.inrat.name} подсоединено")
            self.device_connected.emit()
            return
        logger.debug(f"Не удалось открыть {self.inrat.name}")
        self.inrat = None



    def start(self):
        """ запуск обработки очереди """
        # очистка очередей
        while not self._input_queue.empty():
            self._input_queue.get_nowait()
        while not self._async_queue.empty():
            self._async_queue.get_nowait()
            self._async_queue.task_done()

        self.process_start()

        if not self._running:
            self._running = True
    def process_start(self):
        """ запуск устройства на регистрацию сигналов """
        future = asyncio.run_coroutine_threadsafe(self.inrat.start_acquisition(self._async_queue), self._loop)
        future.add_done_callback(self._on_device_started)
    def _on_device_started(self, future):
        print(f"Устройство запущено на регистрацию данных - {future=}")
        self.device_started.emit()



    def stop(self):
        """ остановка регистрации сигналов устройством """
        self.process_stop()
    def process_stop(self):
        """ обработка остановки устройства """
        future = asyncio.run_coroutine_threadsafe(self.inrat.stop_acquisition(), self._loop)
        future.add_done_callback(self._on_device_stopped)
    def _on_device_stopped(self, future):
        """ обработка результата завершения задачи остановки устройства """
        print(f"Результат выполнения задачи остановки {future=}")
        self.device_stopped.emit()



    def process_disconnect(self):
        """ обработка отсоединения от устройства """
        future = asyncio.run_coroutine_threadsafe(self.inrat.disconnect(), self._loop)
        future.add_done_callback(self._on_device_disconnected)
    def _on_device_disconnected(self, future):
        """ обработка выполнения отсоединения от устройства """
        logger.info(f"Соединение с {self.inrat.name} закрыто!")
        self.inrat = None
        self.device_disconnected.emit()



    async def process_output(self) -> ECG_DataBlock:
        """ обработка асинхронной очереди от inrat и формирование блоков данных """
        ...