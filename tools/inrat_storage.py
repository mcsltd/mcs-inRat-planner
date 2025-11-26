import datetime
import logging
import os.path
import time

import numpy as np
from PySide6.QtCore import QObject

logger = logging.getLogger(__name__)

class InRatStorage(QObject):

    def __init__(self, path_to_save: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signal = np.array([])
        self.path_to_save = os.path.abspath(path_to_save)
        self.is_recording = True

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

    # def clear(self):
    #     """ Очистка параметров при новой записи """
    #     self.start_time: datetime.datetime | None = None

    def start_recording(self):
        """ Начало записи """
        logger.debug(f"Стартовала запись сигнала, частота={self._fs} Гц, формат={self._format}, место сохранения={self.path_to_save}")
        self.is_recording = True
        self.start_time = time.time()

    def stop_recording(self):
        """ Конец записи """
        logger.debug(f"Остановка записи сигнала")
        self.is_recording = False
        self.start_time: datetime.datetime | None = None

    def accept_data(self, signal):
        """ Принять данные для сохранения """
        if not self.is_recording:
            return

        logger.debug(f"Получены данные: {len(signal)}")
