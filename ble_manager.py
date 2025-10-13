import asyncio
import logging
from logging import Logger
from uuid import UUID

from PySide6.QtCore import Signal, QObject

from constants import RecordStatus
from device.ble_scanner import find_device
from device.emgsens import EmgSens
from device.emgsens.constants import ScaleAccel, SamplingRate, EventType, Channel, ScaleGyro
from device.emgsens.structures import Settings
from storage import StorageData
from structure import ScheduleData

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SEC = 5
DEFAULT_SETTING_EMG = Settings(
        DataRateEMG=SamplingRate.HZ_1000.value,
        AveragingWindowEMG=10,
        FullScaleAccelerometer=ScaleAccel.G_0.value,
        FullScaleGyroscope=ScaleGyro.DPS_125.value,
        EnabledChannels=Channel.EMG,
        EnabledEvents=EventType.DISABLE,
        ActivityThreshold=1,
    )


class BLEManager(QObject):

    signal_stop_acquisition = Signal(ScheduleData, UUID, str)
    signal_error_recording = Signal(ScheduleData, UUID, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_storage = StorageData()

    async def start_recording(self, schedule: ScheduleData, record_id: UUID):
        """ Запуск устройства на запись """

        emg_queue = asyncio.Queue()
        event_start = asyncio.Event()

        self.data_storage.setup(
            data_queue=emg_queue,
            freq=schedule.sampling_rate,
            file_format=schedule.file_format,
            event_consume=event_start
        )

        task_save = asyncio.create_task(
            self.data_storage.consume(record_id=record_id, device_name=schedule.device.ble_name)
        )

        task_read = asyncio.create_task(
            self.start_emg_acqusition(
                ble_name=schedule.device.ble_name, emg_queue=emg_queue, duration=schedule.sec_duration, event=event_start
            )
        )
        await asyncio.gather(task_read, task_save)

        file_name = task_save.result()
        status = task_read.result()

        if status == RecordStatus.ERROR.value:
            self.signal_error_recording.emit(schedule, record_id, status)

        elif status == RecordStatus.OK.value:
            self.signal_stop_acquisition.emit(schedule, record_id, file_name)


    async def start_emg_acqusition(self, ble_name, emg_queue, duration, event):
        ble_device, _ = await find_device(
            timeout=DEFAULT_TIMEOUT_SEC,
            template=ble_name
        )

        device = EmgSens(ble_device)

        try:
            if await device.connect(timeout=10):
                if await device.start_emg_acquisition(
                        emg_queue=emg_queue,
                        settings=DEFAULT_SETTING_EMG
                ):
                    t = duration
                    await asyncio.sleep(t)
            status = RecordStatus.OK.value

        except Exception as e:
            logger.error(f"Application error: {e}")
            event.set()
            status = RecordStatus.ERROR.value

        finally:
            await device.disconnect()
            event.set()

        return status