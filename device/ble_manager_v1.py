import asyncio
import datetime
import logging
import threading
import time
import uuid
from threading import Thread
from dataclasses import dataclass, field

import bleak
from PySide6.QtCore import QObject
from uuid import UUID

from bleak import BLEDevice, BleakScanner
from sqlalchemy.util import await_only

from device.ble_scanner import find_device
from device.emgsens import EmgSens
from device.emgsens.constants import EventType, Channel, ScaleGyro, ScaleAccel, SamplingRate
from device.emgsens.structures import Settings
from device.inrat.inrat import InRat
from structure import DeviceData

logger = logging.getLogger(__name__)

@dataclass
class RecordingTaskData:
    device: DeviceData
    start_time: datetime.datetime
    finish_time: datetime.datetime
    id: UUID = field(default_factory=uuid.uuid4)

SCAN_TIMEOUT = 0.1
CONNECTION_TIMEOUT = 5

MAX_COUNT_ATTEMPT_CONNECTION = 5

class BleManager(QObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_running = False

        self._recording_tasks: list[RecordingTaskData] = []             # задачи для записи
        self._acquisition_tasks: dict[UUID, asyncio.Task] = {}          # запущенные задачи на получение данных
        self._connected_devices: dict[UUID, EmgSens | InRat] = {}       # подключенные устройства
        self._device_queues: dict[UUID, asyncio.Queue] = {}             # очередь для устройства

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

            await self._process_new_task()  # обработка новых задач записи
            # await self._monitoring_connected_device() # мониторинг подключенных устройств

            await asyncio.sleep(0.1)

    async def _process_new_task(self) -> None:
        """ Обработка новых задач на подключение """
        while len(self._recording_tasks) != 0:
            recording_task = self._recording_tasks.pop()

            # ToDo: обработка на случай уже подключенного или подключаемого устройства

            # запуск подключения и получения данных с устройства на фоне
            asyncio.create_task(
                self._connect_and_maintain_device(recording_task)
            )

    async def _connect_and_maintain_device(self, task: RecordingTaskData):
        """ Подключение к устройству и поддержание соединения """
        device_id = task.device.id
        device_name = task.device.ble_name

        while self.is_running and device_id not in self._connected_devices:
            try:
                logger.info(f"Попытка подключения к устройству {device_name}")
                ble_device = await self._find_device_by_name(device_name)

                if ble_device is None:
                    logger.debug(f"Устройство {device_name} не найдено")
                    # нужен ли тут await asyncio.sleep(5)?
                    continue

                emg_sens = EmgSens(ble_device)
                if await emg_sens.connect(CONNECTION_TIMEOUT):
                    logger.info(f"Успешное подключение к устройств {device_name}")

                    # добавляем новое подключенное устройство
                    self._connected_devices[device_id] = emg_sens
                    self._device_queues[device_id] = asyncio.Queue()

                    acquisition_task = asyncio.create_task(self._start_data_acquisition(emg_sens, task))
                    self._acquisition_tasks[device_id] = acquisition_task

                    break
                else:
                    logger.warning(f"Не удалось подключиться к устройству {device_name}")
            except Exception as exc:
                logger.error(f"Ошибка при подключении к {device_name}: {exc}")


    async def _start_data_acquisition(self, emg_sens: EmgSens, task: RecordingTaskData):
        """ Запуск сбора данных с устройства и их обработка """

        base_settings = Settings(
            DataRateEMG=SamplingRate.HZ_1000.value,
            AveragingWindowEMG=10,
            FullScaleAccelerometer=ScaleAccel.G_0.value,
            FullScaleGyroscope=ScaleGyro.DPS_125.value,
            EnabledChannels=Channel.EMG,
            EnabledEvents=EventType.DISABLE,
            ActivityThreshold=1)

        data_queue = asyncio.Queue()
        try:
            if await emg_sens.start_emg_acquisition(settings=base_settings, emg_queue=data_queue):
                logger.info(f"Сбор данных запущен для устройства {task.device.ble_name}")

                # обработка входящих данных
                while self.is_running and datetime.datetime.now() < task.finish_time and emg_sens.is_connected:
                    try:
                        data = await asyncio.wait_for(data_queue.get(), timeout=1.0)
                        data_queue.task_done()

                    except asyncio.TimeoutError:
                        continue

                    except Exception as exp:
                        logger.error(f"Ошибка обработки данных от {task.device.ble_name}")
                        break

        except Exception as e:
            logger.error(f"Ошибка в задаче сбора данных для {task.device.ble_name}: {e}")
        finally:
            await self._cleanup_device(task.device.ble_name)     # Очистка при завершении


    async def _cleanup_device(self, device_id):
        """ Отключение и очистка устройства """
        logger.debug(f"Отключение от устройства: {self._connected_devices[device_id].name}")

        await self._connected_devices[device_id].disconnect()

        if not self._connected_devices[device_id].is_connected:
            device = self._connected_devices.pop(device_id)
            logger.debug(f"Устройство {device.name} отключено и удалено из списка подключенных устройств")

        self._connected_devices.pop(device_id)

    async def _find_device_by_name(self, device_name: str) -> BLEDevice | None:
        devices = await BleakScanner.discover(timeout=SCAN_TIMEOUT)
        for d in devices:
            if d.name and device_name in d.name:
                logger.info(f"Найдено устройство: {d.name} ({d.address})")
                return d
            logger.warning(f"Устройство {device_name} не найдено")
            return None
        return None


    def stop(self):
        """ Остановка BLE менеджера """
        if not self.is_running:
            logger.debug("BLE менеджер не был запущен, не могу выполнить остановку")

        self.is_running = False
        self._work_thread.join(timeout=0.1) # ожидание остановки потока
        if self._work_thread.is_alive():
            raise ValueError("Поток не остановлен...")

        logger.info("BLE менеджер остановлен")

    def add_task(self, task: RecordingTaskData):
        """ Добавить устройство в очередь на обработку """
        logger.info(f"Добавлено устройство {task.device.ble_name} в очередь на обработку")
        self._recording_tasks.append(task)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    manager = BleManager()
    manager.start()

    ft = datetime.datetime.now() + datetime.timedelta(minutes=1)
    d_1144 = None
    d_1102 = None

    # while datetime.datetime.now() < ft:
    while True:

        if d_1144 is None:
            # add device 1144
            d_1144 = DeviceData(
                serial_number=1144,
                ble_name="EMG-SENS-1144",
                model="EMGsens"
            )
            task_1144 = RecordingTaskData(
                device=d_1144,
                start_time=datetime.datetime.now(),
                finish_time=datetime.datetime.now() + datetime.timedelta(seconds=20)
            )
            manager.add_task(task_1144)

        time.sleep(0.1)

        # if d_1102 is None:
        #     # add device 1102
        #     d_1102 = DeviceData(
        #         serial_number=1102,
        #         ble_name="EMG-SENS-1102",
        #         model="EMGsens"
        #     )
        #     task_1102 = RecordingTaskData(
        #         device=d_1102,
        #         start_time=datetime.datetime.now(),
        #         finish_time=datetime.datetime.now() + datetime.timedelta(seconds=40)
        #     )
        #
        #     manager.add_task(task_1102)
        #     time.sleep(1)

    print("Текущее кол-во потоков:", threading.active_count())
    manager.stop()