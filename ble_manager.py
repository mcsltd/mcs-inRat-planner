import asyncio
import logging
from logging import Logger

from PySide6.QtCore import Signal, QObject

from constants import RecordStatus
from device.ble_scanner import find_device
from device.emgsens import EmgSens
from device.emgsens.constants import ScaleAccel, SamplingRate, EventType, Channel, ScaleGyro
from device.emgsens.structures import Settings
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

    signal_info = Signal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start_recording(self, schedule: ScheduleData):
        """ Запуск устройства на запись """
        ble_device, _ = await find_device(
            timeout=DEFAULT_TIMEOUT_SEC,
            template=schedule.device.ble_name
        )
        device = EmgSens(ble_device)
        emg_queue = asyncio.Queue()

        try:
            if await device.connect(timeout=10):

                if await device.start_emg_acquisition(
                        emg_queue=emg_queue,
                        settings=DEFAULT_SETTING_EMG
                ):
                    t = schedule.sec_duration
                    await asyncio.sleep(t)

        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await device.disconnect()

        self.signal_info.emit(
            {"status": RecordStatus.OK, "id": schedule.id, "duration": schedule.sec_duration}
        )
