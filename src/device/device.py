import asyncio
import copy
import logging
import time
import numpy as np

from asyncio import AbstractEventLoop, Future
from PySide6.QtCore import QObject, Signal
from bleak import BLEDevice, BleakScanner

from src.device.inrat_v1.constants import Pkt
from src.device.inrat_v1.inrat import inRat

logger = logging.getLogger(__name__)


class ECG_DataBlock:
    def __init__(self, ecg=1):
        self.sample_counter = 0
        self.sample_rate = 500.0
        self.ecg_channels = np.zeros((ecg, Pkt.SamplesCountEcg))
        self.start_time = None

class inRatDevice(QObject):

    device_connected = Signal(object)
    device_disconnected = Signal(object)
    device_data_received = Signal(object)
    device_stopped = Signal(object)

    def __init__(self, loop: AbstractEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ecg_data = ECG_DataBlock()

        self._loop: AbstractEventLoop = loop
        self._inrat: inRat | None = None

        self._is_running = False
        self._queue_signal = asyncio.Queue()
        self._queue_event = asyncio.Queue()

    def process_connect(self, ble_device: BLEDevice, wait: int = 10):
        """ соединение с устройством """
        self._inrat = inRat(ble_device)
        future = asyncio.run_coroutine_threadsafe(self._inrat.connect(wait), self._loop)
        future.add_done_callback(self.device_connected.emit)

    def process_start(self):
        """ запуск устройства """
        if not self._inrat:
            return

        if not self._inrat.is_connected:
            return

        # future = asyncio.run_coroutine_threadsafe(
        #     self._inrat.start_acquisition(qevent=self._queue_event, qsignal=self._queue_signal), self._loop
        # )

        future = asyncio.run_coroutine_threadsafe(
            self._inrat.start_acquisition(qevent=None, qsignal=self._queue_signal), self._loop
        )


        future = asyncio.run_coroutine_threadsafe(
            self.process_acquisition(), self._loop
        )

    async def process_acquisition(self):
        """ обработка получения сигналов и событий """
        self._is_running = True
        while self._is_running:
            # ev = await self._queue_event.get()
            # self._queue_event.task_done()
            # print(f"{ev=}")

            sig = await self._queue_signal.get()

            self._ecg_data.ecg_channels = sig["signal"]
            self._ecg_data.sample_counter = sig["counter"]
            self._ecg_data.start_time = sig["start_time"]

            ecg_data = copy.copy(self._ecg_data)
            self.device_data_received.emit(ecg_data)

            self._queue_signal.task_done()

    def process_stop(self):
        """ остановка устройства """
        self._is_running = False
        future = asyncio.run_coroutine_threadsafe(
            self._inrat.stop_acquisition(), self._loop
        )
        future.add_done_callback(self.on_device_stopped)

    def on_device_stopped(self, future: Future):
        """ остановка получения данных с устройства """
        self.device_stopped.emit(future)

    def process_disconnect(self):
        """ отсоединение от устройства """
        if not self._inrat:
            return

        future = asyncio.run_coroutine_threadsafe(self._inrat.disconnect(), self._loop)
        future.add_done_callback(self.on_device_disconnected)

    def on_device_disconnected(self, future):
        self.device_disconnected.emit(future)


async def main():
    ble_device = await BleakScanner.find_device_by_name(name="inRat-1-1022")


    if ble_device:
        loop = asyncio.get_event_loop()
        device = Device(loop=loop)
        device.process_connect(ble_device=ble_device)
        await asyncio.sleep(30)
        device.process_start()
        await asyncio.sleep(30)
        device.process_stop()
        await asyncio.sleep(10)
        device.process_disconnect()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(), debug=True)