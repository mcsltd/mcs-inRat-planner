import datetime
import logging
import os.path
import time
from uuid import UUID

import numpy as np
import wfdb
from PySide6.QtCore import QObject, Signal
from pyedflib import EdfWriter
from transliterate import detect_language, translit

from src.constants import RecordStatus
from src.structure import RecordData

logger = logging.getLogger(__name__)

class InRatStorage(QObject):

    signal_record_saved = Signal(object)

    def __init__(
            self,
            path_to_save: str, device_name: str, object_name: str, experiment_name:str, schedule_id: UUID,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.signal = np.array([])
        self.path_to_save = os.path.abspath(path_to_save)
        self.is_recording = True

        self._schedule_id: UUID = schedule_id
        self._object_name: str = object_name
        self._device_name: str = device_name
        self._experiment_name: str = experiment_name

        self._fs: int | None = None
        self._format: str | None = None
        self.start_time: float | None = None

    def set_sampling_rate(self, freq: int):
        """ Установка новой частоты оцифровки """
        logger.info(f"Изменена частота оцифровки: {self._fs} -> {freq}")
        self._fs = freq

    def set_format(self, frmt: str):
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
        datetime_st = datetime.datetime.fromtimestamp(self.start_time)

        filename = self.get_record_filename(
            obj_name=self._object_name, experiment=self._experiment_name,
            start_time=datetime_st,
        )
        os.makedirs(write_dir, exist_ok=True)

        if self._format == "WFDB":
            self.save_to_wfdb(filename=filename, write_dir=write_dir)

        if self._format == "EDF":
            filename = f"{write_dir}\\{filename}.edf"
            self.save_to_edf(filename=filename)
        
        # оповещение окна ручного режима о сделанной записи
        record_data = RecordData(datetime_start=datetime_st, sec_duration=int(len(self.signal) / self._fs),
                                 file_format=self._format, sampling_rate=self._fs, status=RecordStatus.OK.value,
                                 schedule_id=self._schedule_id, path=filename)
        self.signal_record_saved.emit(record_data)

        # сброс
        self.start_time: datetime.datetime | None = None
        self.signal = np.array([])

    def accept_data(self, signal):
        """ Принять данные для сохранения """
        if not self.is_recording:
            return

        self.signal = np.append(self.signal, signal)
        logger.debug(f"Получены данные: {len(signal)}")

    def save_to_wfdb(self, filename: str, write_dir: str):
        """ Сохранение полученного сигнала в WFDB формате """
        try:
            wfdb.io.wrsamp(
                record_name=filename, fs=self._fs, units=["uV"], p_signal=self.signal[np.newaxis].T,
                sig_name=["ECG"], write_dir=write_dir, base_datetime=datetime.datetime.fromtimestamp(self.start_time)
            )
        except Exception as exc:
            raise ValueError(f"Возникла ошибка записи в файл: {exc}")
        else:
            logger.info(f"Файл в формате WFDB {filename} успешно записан!")


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
                'label': "ECG", 'dimension': "uV", 'sample_frequency': self._fs,
                'physical_max': physical_max, 'physical_min': physical_min, 'digital_max': 32767, 'digital_min': -32768,
            }
            writer.setSignalHeader(0, channel_info)
            writer.setEquipment("None" if self._device_name is None else self._device_name)
            writer.writeSamples(edf_signal[np.newaxis])
            writer.close()
        except Exception as exc:
            raise ValueError(f"Возникла ошибка записи в файл: {exc}")
        else:
            logger.info(f"Файл в формате EDF {filename} успешно записан!")


    def get_record_filename(self, experiment: str, obj_name: str, start_time: datetime.datetime) -> str:
        experiment = self.to_latin(experiment)
        obj_name = self.to_latin(obj_name)
        str_start_date = f"{start_time.year}-{start_time.month}-{start_time.day}"
        str_start_time = f"{start_time.hour}-{start_time.minute}-{start_time.second}"
        filename = f"{experiment}_{obj_name}_{str_start_date}_{str_start_time}"
        return filename

    @staticmethod
    def to_latin(string: str) -> str:
        if detect_language(string) == "ru":
            string = translit(string, reversed=True)
            string = string.replace("'", "")
        return string