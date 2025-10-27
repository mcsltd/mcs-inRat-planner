import asyncio
import datetime
import logging
import threading
import time
import uuid
from threading import Thread
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal
from uuid import UUID

from bleak import BLEDevice, BleakScanner

from constants import RecordStatus
from device.emgsens import EmgSens
from device.emgsens.constants import EventType, Channel, ScaleGyro, ScaleAccel, SamplingRate
from device.emgsens.structures import Settings
from device.inrat.inrat import InRat
from storage_v1 import Storage
from structure import DeviceData, RecordingTaskData, RecordData

logger = logging.getLogger(__name__)

SCAN_TIMEOUT = 0.1
CONNECTION_TIMEOUT = 5

MAX_COUNT_ATTEMPT_CONNECTION = 5

class BleManager(QObject):

    # for main window
    signal_record_result = Signal(RecordData)

    # for devices
    signal_start_acquisition = Signal(UUID)
    signal_data_received = Signal(UUID, dict)
    signal_stop_acquisition = Signal(UUID)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_running = False

        self.storage = Storage()

        # соединение сигналами Storage и BLEManager
        self.signal_start_acquisition.connect(self.storage.add_recording_task)
        self.signal_data_received.connect(self.storage.accept_data)
        self.signal_stop_acquisition.connect(self.storage.stop_recording_task)
        self.storage.signal_success_save.connect(self.handle_success_record_result)

        self._recording_tasks: list[RecordingTaskData] = []             # задачи для записи
        self._acquisition_tasks: dict[UUID, asyncio.Task] = {}          # запущенные задачи на получение данных
        self._connected_devices: dict[UUID, EmgSens | InRat] = {}       # словарь с подключенными устройствами
        self._device_queues: dict[UUID, asyncio.Queue] = {}             # очередь для получения данных с устройства

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

            await self._process_new_task()              # обработка новых задач записи
            # await self._monitoring_connected_device() # мониторинг подключенных устройств

            await asyncio.sleep(0.1)

    async def _process_new_task(self) -> None:
        """ Обработка новых задач на подключение """
        while len(self._recording_tasks) != 0:
            recording_task = self._recording_tasks.pop()
            device_id = recording_task.device.id

            # ToDo: обработка на случай уже подключенного или подключаемого устройства
            if device_id in self._connected_devices:
                logger.warning(f"Устройство {recording_task.device.ble_name} уже подключено или в процессе подключения")
                continue

            # запуск подключения и получения данных с устройства на фоне
            asyncio.create_task(
                self._device_connect_and_data_acquisition(recording_task)
            )

    async def _device_connect_and_data_acquisition(self, task: RecordingTaskData):
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

                    self.signal_start_acquisition.emit(task)   # активация сигнала о начале записи

                    # создание задачи на получение данных с устройства
                    acquisition_task = asyncio.create_task(self._start_data_acquisition(emg_sens, task))
                    self._acquisition_tasks[device_id] = acquisition_task
                    break
                else:
                    logger.warning(f"Не удалось подключиться к устройству {device_name}")
            except Exception as exc:
                logger.error(f"Ошибка при подключении к {device_name}: {exc}")

                record_data = task.get_result_record(duration=0, status=RecordStatus.ERROR) # ошибка записи
                self.signal_record_result.emit(record_data)

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

        device_id = task.device.id
        data_queue = self._device_queues[device_id]

        try:
            if await emg_sens.start_emg_acquisition(settings=base_settings, emg_queue=data_queue):
                logger.info(f"Сбор данных запущен для устройства {task.device.ble_name}")

                # обработка входящих данных
                while self.is_running and emg_sens.is_connected and datetime.datetime.now() < task.finish_time:
                    try:
                        data = await asyncio.wait_for(data_queue.get(), timeout=1.0)
                        self.signal_data_received.emit(device_id, data)
                        data_queue.task_done()

                    except asyncio.TimeoutError:
                        continue

                    except Exception as exp:
                        logger.error(f"Ошибка обработки данных с устройства {task.device.ble_name}")

                        self.signal_stop_acquisition.emit(device_id)

                        break
        except Exception as e:

            record_data = task.get_result_record(duration=0, status=RecordStatus.ERROR)  # ошибка записи
            self.signal_record_result.emit(record_data)

            logger.error(f"Ошибка в задаче сбора данных для {task.device.ble_name}: {e}")
        finally:
            self.signal_stop_acquisition.emit(device_id)
            await self._cleanup_device(device_id)     # Очистка при завершении

    async def _cleanup_device(self, device_id: UUID):
        """ Очистка ресурсов устройства """
        try:

            # убрать device_id из словаря подключенных устройств
            if device_id in self._connected_devices:
                emg_sens = self._connected_devices[device_id]
                if emg_sens.is_connected:
                    await emg_sens.stop_acquisition()
                    await emg_sens.disconnect()
                del self._connected_devices[device_id]

            # отмена задачи на получение данных
            if device_id in self._acquisition_tasks:
                self._acquisition_tasks[device_id].cancel()
                try:
                    await self._acquisition_tasks[device_id]
                except asyncio.CancelledError:
                    pass
                del self._acquisition_tasks[device_id]

            # удаление очереди для emgsens с device_id
            if device_id in self._device_queues:
                self._device_queues.pop(device_id)

            logger.info(f"Ресурсы устройства {device_id} очищены")

        except Exception:
            logger.error("Возникла ошибка очистки ресурсов для устройств....")

    async def _find_device_by_name(self, device_name: str) -> BLEDevice | None:
        """ Поиск устройств по имени """
        try:
            devices = await BleakScanner.discover(timeout=SCAN_TIMEOUT)
            for d in devices:
                if d.name and device_name in d.name:
                    logger.info(f"Найдено устройство: {d.name} ({d.address})")
                    return d

                logger.warning(f"Устройство {device_name} не найдено")
                return None

            return None
        except Exception as exc:
            logger.error(f"Ошибка при поиске устройства: {device_name}: {exc}")
            return None

    def stop(self):
        """ Остановка BLE менеджера """
        if not self.is_running:
            logger.debug("BLE менеджер не был запущен, не могу выполнить остановку")

        # asyncio.create_task(self.disconnect_all_devices())

        self.is_running = False
        self._work_thread.join(timeout=0.1) # ожидание остановки потока
        if self._work_thread.is_alive():
            raise ValueError("Поток не остановлен...")

        logger.info("BLE менеджер остановлен")

    def add_task(self, task: RecordingTaskData):
        """ Добавить устройство в очередь на обработку """
        logger.info(f"Добавлено устройство {task.device.ble_name} в очередь на обработку")
        self._recording_tasks.append(task)

    async def disconnect_all_devices(self):
        """ Отключение всех устройств """
        devices_id = list(self._connected_devices.keys())
        for idx in devices_id:
            await self._cleanup_device(idx)

    def handle_success_record_result(self, record_data: RecordData):
        self.signal_record_result.emit(record_data)

if __name__ == "__main__":
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    # )

    manager = BleManager()
    manager.start()

    ft = datetime.datetime.now() + datetime.timedelta(minutes=1)
    d_1144 = None
    d_1102 = None

    while datetime.datetime.now() < ft:
    # while True:

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
                finish_time=datetime.datetime.now() + datetime.timedelta(seconds=30)
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
        #         finish_time=datetime.datetime.now() + datetime.timedelta(seconds=20)
        #     )
        #
        #     manager.add_task(task_1102)

    print("Текущее кол-во потоков:", threading.active_count())
    manager.stop()