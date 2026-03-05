import asyncio
import concurrent
import numpy as np
import logging
import copy
import queue
from asyncio import AbstractEventLoop, to_thread
from threading import Lock, Thread

from PySide6.QtCore import QObject, Signal
from bleak import BLEDevice

from src.device.inrat_v1.constants import Pkt
from src.device.inrat_v1.inrat import inRat

logger = logging.getLogger(__name__)

class EcgDataBlock:
    def __init__(self):
        self.sample_counter = 0
        self.ecg_channels = np.zeros(Pkt.SamplesCountEcg)


class inRatDevice(QObject):

    device_connected = Signal()
    device_started = Signal()
    device_stopped = Signal()
    device_disconnected = Signal()

    def __init__(self, loop: AbstractEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.inrat: inRat | None = None
        self.ecg_data = EcgDataBlock()

        self._loop: AbstractEventLoop = loop
        self._receivers = []
        self._running = False
        # self._lock = Lock()
        self._input_queue = queue.Queue()
        self._async_queue = asyncio.Queue()
        self._work: concurrent.futures.Future | None = None


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

        # запуск всех прикрепленных классов-получателей
        for receiver in self._receivers:
            receiver.start()

        self.process_start()
        if not self._running:
            self._running = True
            self._work = asyncio.run_coroutine_threadsafe(self._async_worker_thread(), self._loop)

    def process_start(self):
        """ запуск устройства на регистрацию сигналов """
        future = asyncio.run_coroutine_threadsafe(self.inrat.start_acquisition(self._async_queue), self._loop)
        future.add_done_callback(self._on_device_started)
    def _on_device_started(self, future):
        print(f"Устройство запущено на регистрацию данных")
        self.device_started.emit()
    async def _async_worker_thread(self):
        while self._running:
            data = await self.process_output()
            if data:
                for receiver in self._receivers:
                    receiver._transmit_data(copy.deepcopy(data))
            await asyncio.sleep(0.001)

    async def process_output(self):
        """ обработка асинхронной очереди от inrat и формирование блоков данных """
        data = await self._async_queue.get()
        self._async_queue.task_done()
        if data["type"] == "event":
            event_block = self.process_event(data)
            return event_block
        if data["type"] == "signal":
            signal_block = self.process_signal(data)
            return signal_block
        return None

    def process_event(self, event):
        print(f"{event=}")
        return event
    def process_signal(self, signal):
        self.ecg_data.sample_counter = signal["counter"]
        self.ecg_data.ecg_channels = signal["signal"]
        return copy.copy(self.ecg_data)


    def stop(self):
        """ остановка регистрации сигналов устройством """
        self._running = False
        if not self._work.done:
            self._work.cancel()
        self.process_stop()
        for receiver in self._receivers:
            receiver.stop()
    def process_stop(self):
        """ обработка остановки устройства """
        future = asyncio.run_coroutine_threadsafe(self.inrat.stop_acquisition(), self._loop)
        future.add_done_callback(self._on_device_stopped)
    def _on_device_stopped(self, future):
        """ обработка результата задачи остановки устройства """
        print(f"Регистрация данных с устройства остановлена")
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


    def add_receiver(self, receiver):
        if self._running:
            receiver.start()
        self._receivers.append(receiver)