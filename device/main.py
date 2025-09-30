import asyncio
import datetime
import logging
import numpy as np

from sqlalchemy.util import counter
from pyedflib import EdfWriter

from constants import Formats
from device.emgsens.constants import SamplingRate, ScaleGyro, Channel, ScaleAccel, EventType
from emgsens.emg_sens import EmgSens
from ble_scanner import find_device
from device.emgsens.structures import Settings

logger = logging.getLogger(__name__)


class QueueDataConsumer:    # заготовка

    def __init__(self):
        self.freq: int | None = None
        self.data_queue: asyncio.Queue | None = None
        self.data_buffer: dict | None = None
        self.file_format = None
        self._event_consume: asyncio.Event | None = None

    def setup(
            self,
            data_queue: asyncio.Queue, event_consume: asyncio.Event,
            freq: int, file_format: str
    ):
        self.data_queue: asyncio.Queue = data_queue
        self.freq = freq
        self.file_format = file_format
        self.data_buffer = None
        self._event_consume = event_consume

    async def consume(self):
        if self.data_queue is None:
            raise TypeError("Queue is not initialized")
        if self._event_consume is None:
            raise TypeError("Event consume is not initialized")

        logger.debug("Start consuming data from queue")
        self._is_consuming = True

        # get signals
        data = await self.data_queue.get()
        self.data_queue.task_done()

        # init data buffer
        if self.data_buffer is None:
            headers = list(data.keys())
            headers.remove("counter")
            self.data_buffer = dict.fromkeys(headers, None)
            # extract signals
            for key in data.keys():
                if key != "counter":
                    self.data_buffer[key] = data[key]

        logger.debug("Consume data from queue")
        while not self._event_consume.is_set():
            # data = await self.data_queue.get()

            try:
                # get signals
                data = await asyncio.wait_for(self.data_queue.get(), timeout=0.1)

                # extract signals
                for key in data.keys():
                    if key != "counter":
                        self.data_buffer[key] = np.append(self.data_buffer[key], data[key])

                self.data_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing data: {e}")
                if not self.data_queue.empty():
                    self.data_queue.task_done()

        self.save()

    def stop(self):
        logger.debug("Stop consumer...")
        if not self._event_consume.is_set:
            raise ValueError("Event is not set. Can't stop consumer!")

        # self._event_consume = None
        self.freq = None
        self.data_queue = None
        self.data_buffer = None
        self.file_format = None

    def save(self):
        if self.file_format == list(Formats.CSV.value.values())[0]:
            self.save_to_csv()
        if self.file_format == list(Formats.EDF.value.values())[0]:
            self.save_to_edf()
        if self.file_format == list(Formats.WFDB.value.values())[0]:
            self.save_to_wfdb()

    def save_to_edf(self, units: str = "uV", sig_name: str="EMG"):
        logger.debug("Save data to edf.")
        writer = EdfWriter(
            n_channels=1,
            file_name="filename.edf",
        )

        self.signal = np.round(self.data_buffer["emg"] * 1e6, decimals=3)

        margin = 0.15
        signal_max = np.max(self.signal)
        signal_min = np.min(self.signal)
        physical_max = np.round(signal_max * (1 + margin) if signal_max > 0 else signal_max * (1 - margin), decimals=3)
        physical_min = np.round(signal_min * (1 - margin) if signal_min > 0 else signal_min * (1 + margin), decimals=3)

        channel_info = {
            'label': sig_name,
            'dimension': units,
            'sample_frequency': 1000,
            'physical_max': physical_max,
            'physical_min': physical_min,
            'digital_max': 32767,
            'digital_min': -32768,
        }
        writer.setSignalHeader(0, channel_info)
        writer.writeSamples(self.signal[np.newaxis])
        writer.close()


    def save_to_wfdb(self):
        logger.debug("Save data to wfdb.")

    def save_to_csv(self):
        logger.debug("Save data to csv.")


async def read_time_data(
        time_start:datetime.datetime, time_finish:datetime.datetime,
        device_name: str, emg_queue: asyncio.Queue, event_start: asyncio.Event
):
    st = Settings(
        DataRateEMG=SamplingRate.HZ_1000.value,
        AveragingWindowEMG=10,
        FullScaleAccelerometer=ScaleAccel.G_0.value,
        FullScaleGyroscope=ScaleGyro.DPS_125.value,
        EnabledChannels=Channel.EMG,
        EnabledEvents=EventType.DISABLE,
        ActivityThreshold=1,
    )

    ble_device, _ = await find_device(timeout=10, template=device_name)
    device = EmgSens(ble_device)
    await device.connect()

    t = (time_finish - time_start).total_seconds()
    await device.get_emg(emg_queue=emg_queue, settings=st)
    await asyncio.sleep(t)
    event_start.set()   # stop consumer
    await device.disconnect()



async def main():
    device_name = "EMG-SENS-1144"

    emg_queue = asyncio.Queue()
    event_start = asyncio.Event()

    time_start = datetime.datetime.now()
    time_finish = time_start + datetime.timedelta(seconds=15)

    data_storage = QueueDataConsumer()
    read_task = asyncio.create_task(read_time_data(
        time_start=time_start, time_finish=time_finish,
        device_name=device_name,
        emg_queue=emg_queue, event_start=event_start))

    data_storage.setup(data_queue=emg_queue, freq=1000, file_format="EDF", event_consume=event_start)

    save_task = asyncio.create_task(data_storage.consume())
    await asyncio.gather(read_task, save_task)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main())