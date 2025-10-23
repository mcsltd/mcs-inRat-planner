import asyncio
import logging
import os

import numpy as np
from PySide6.QtCore import QObject
from pyedflib import EdfWriter

from constants import Formats

logger = logging.getLogger(__name__)

class StorageData(QObject):    # заготовка

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    async def consume(self, device_name, record_id):
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

        file_name = self.save(record_id, device_name)
        print(f"{file_name=}")
        return file_name

    def stop(self):
        logger.debug("Stop consumer...")
        if not self._event_consume.is_set:
            raise ValueError("Event is not set. Can't stop consumer!")

        # self._event_consume = None
        self.freq = None
        self.data_queue = None
        self.data_buffer = None
        self.file_format = None

    def save(self, record_id, device_name) -> str | None:
        write_dir = f".\\data\\{device_name}\\"
        path_to_file = None

        if self.file_format == list(Formats.CSV.value.values())[0]:
            write_dir += "CSV\\"
            path_to_file = self.save_to_csv()

        if self.file_format == list(Formats.EDF.value.values())[0]:
            write_dir += "EDF\\"
            # create dir for saving files with selected format
            os.makedirs(write_dir, exist_ok=True)
            path_to_file = self.save_to_edf(record_id, write_dir)

        if self.file_format == list(Formats.WFDB.value.values())[0]:
            write_dir += "WFDB\\"
            path_to_file = self.save_to_wfdb()

        return path_to_file

    def save_to_edf(self, record_id, write_dir, units: str = "uV", sig_name: str="EMG") -> str | None:
        logger.debug("Save data to edf.")
        file_name = write_dir + f"{record_id}.edf"

        try:
            writer = EdfWriter(
                n_channels=1,
                file_name=file_name,
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
        except Exception as exp:
            logger.debug(f"Ошибка создания EDF файла - {file_name}: {exp}")
            return None
        else:
            logger.debug(f"Файл EDF успешно создан - {file_name}")
            return file_name

    def save_to_wfdb(self):
        logger.debug("Save data to wfdb.")

    def save_to_csv(self):
        logger.debug("Save data to csv.")