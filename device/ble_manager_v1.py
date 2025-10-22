import asyncio
import logging
import time
from threading import Thread

from PySide6.QtCore import QObject

from structure import DeviceData


logger = logging.getLogger(__name__)

class BleManager(QObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_running = False
        self._devices_info: list[DeviceData] = []
        self._work_thread: None | Thread  = None
        self._async_loop: None | asyncio.AbstractEventLoop = None

    def start(self):
        """ Запуск BLE менеджера для работы с устройствами """
        if self.is_running:
            logger.warning("BLE менеджер уже запущен")
            return

        self.is_running = True
        self._work_thread = Thread(target=self._run_async_loop)
        self._work_thread.start()

        logger.info("BLE менеджер запущен")

    def _run_async_loop(self):
        """ Создание асинхронного цикла событий и запуск в нём цикла обработки """
        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)
        self._async_loop.run_until_complete(self._processing_loop())

    async def _processing_loop(self):
        """
        Главный цикл, в котором происходит обработка очереди из устройств.
        Обработка включает в себя: 1) поиск; 2) соединение; 3) получение данных; 4) отключение
        """
        while self.is_running:
            logger.info("Идёт поиск устройства ...")
            await asyncio.sleep(1)
            logger.info("Идёт соединение с устройством ...")
            await asyncio.sleep(1)
            logger.info("Идёт получение данных с устройства ...")
            await asyncio.sleep(1)
            logger.info("Отключение от устройства ...")

    def stop(self):
        """ Остановка BLE менеджера """
        if not self.is_running:
            logger.debug("BLE менеджер не был запущен, не могу выполнить остановку")

        self.is_running = False
        self._work_thread.join(timeout=0.1) # ожидание остановки потока
        if self._work_thread.is_alive():
            raise ValueError("Поток не остановлен...")

        logger.info("BLE менеджер остановлен")

    def add_device(self, device_info: DeviceData):
        """ Добавить устройство в очередь на обработку """
        logger.info("Добавлено устройство в очередь на обработку")
        self._devices_info.append(device_info)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    manager = BleManager()
    manager.start()

    time.sleep(10)

    manager.stop()