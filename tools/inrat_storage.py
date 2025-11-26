import datetime
import logging
import os.path
import time
from pathlib import Path

import numpy as np
import wfdb
from PySide6.QtCore import QObject
from pyedflib import EdfWriter

logger = logging.getLogger(__name__)

class InRatStorage(QObject):

    def __init__(self, path_to_save: str, device_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signal = np.array([])
        self.path_to_save = os.path.abspath(path_to_save)
        self.is_recording = True

        self._device_name = device_name
        self._fs = None
        self._format = None
        self.start_time: float | None = None

    def set_sampling_rate(self, freq):
        """ Установка новой частоты оцифровки """
        logger.info(f"Изменена частота оцифровки: {self._fs} -> {freq}")
        self._fs = freq

    def set_format(self, frmt):
        """ Изменение формата записи в файл"""
        logger.info(f"Изменен формат записи: {self._format} -> {frmt}")
        self._format = frmt

    def set_save_dir(self, path: str):
        """ Установка нового пути сохранения записей сигнала """
        logger.info(f"Изменено место сохранения записей: {self.path_to_save} -> {path}")
        if os.path.isdir(path):
            self.path_to_save = path
        else:
            raise ValueError("Dir is not exists!")


    def start_recording(self):
        """ Начало записи """
        logger.debug(f"Стартовала запись сигнала, частота={self._fs} Гц, формат={self._format}, место сохранения={self.path_to_save}")
        self.is_recording = True
        self.start_time = time.time()

    def stop_recording(self):
        """ Конец записи """
        logger.debug(f"Остановка записи сигнала")
        self.is_recording = False

        write_dir = f"{self.path_to_save}\\{self._device_name}"
        filename = self.get_file_name()
        os.makedirs(write_dir, exist_ok=True)
        if self._format == "WFDB":
            self.save_to_wfdb(record_name=filename, write_dir=write_dir)
        if self._format == "EDF":
            filename = f"{write_dir}\\{filename}.edf"
            self.save_to_edf(filename=filename)

        # сброс
        self.start_time: datetime.datetime | None = None
        self.signal = np.array([])

    def get_file_name(self):
        start_datetime = datetime.datetime.fromtimestamp(self.start_time)
        str_st:str = str(start_datetime.date()) + "_" + str(start_datetime.time().replace(microsecond=0))
        for v in ["h", "m"]:
            str_st = str_st.replace(":", v, 1)
        str_st += "s"

        dur = int(self.signal.shape[0] / self._fs)
        filename = f"{str_st}_dur_{dur}_sec"
        return filename

    def accept_data(self, signal):
        """ Принять данные для сохранения """
        if not self.is_recording:
            return

        self.signal = np.append(self.signal, signal)

        logger.debug(f"Получены данные: {len(signal)}")

    def save_to_wfdb(self, record_name: str, write_dir: str):
        """ Сохранение полученного сигнала в WFDB формате """
        try:
            wfdb.io.wrsamp(
                record_name=record_name,
                fs=self._fs, units=["uV"], p_signal=self.signal[np.newaxis].T,
                sig_name=["ECG"], write_dir=write_dir, base_datetime=datetime.datetime.fromtimestamp(self.start_time)
            )
        except Exception as exc:
            raise ValueError(f"Возникла ошибка записи в файл: {exc}")
        else:
            logger.info(f"Файл в формате WFDB {record_name} успешно записан!")


    def save_to_edf(self, filename: str):
        """ Сохранение полученного сигнала в EDF формате """
        try:
            writer = EdfWriter(
                n_channels=1,
                file_name=filename,
            )
            edf_signal = np.round(self.signal, decimals=5)

            margin = 0.15
            signal_max = np.max(edf_signal)
            signal_min = np.min(edf_signal)
            physical_max = np.round(signal_max * (1 + margin) if signal_max > 0 else signal_max * (1 - margin), decimals=5)
            physical_min = np.round(signal_min * (1 - margin) if signal_min > 0 else signal_min * (1 + margin), decimals=5)

            channel_info = {
                'label': "ECG",
                'dimension': "uV",
                'sample_frequency': self._fs,
                'physical_max': physical_max,
                'physical_min': physical_min,
                'digital_max': 32767,
                'digital_min': -32768,
            }
            writer.setSignalHeader(0, channel_info)
            writer.setEquipment("None" if self._device_name is None else self._device_name)
            writer.writeSamples(edf_signal[np.newaxis])
            writer.close()
        except Exception as exc:
            raise ValueError(f"Возникла ошибка записи в файл: {exc}")
        else:
            logger.info(f"Файл в формате EDF {filename} успешно записан!")