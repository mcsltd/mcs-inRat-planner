import logging
import threading
from uuid import UUID
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class Storage(QObject):

    signal_save_error = Signal()
    signal_success_save = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        # self._devices_id: list[UUID] = []
        self._data: dict[UUID, list[dict]] = {}

    def start_recording(self, device_id: UUID):
        """ Начало записи данных, приходящих из BleManager """
        if device_id in self._data:
            logging.warning(f"Для устройства c индексом {device_id} уже ведётся запись")
            return

        logger.info(f"Начало записи данных для устройства с индексом {device_id}")
        self._data[device_id] = []

    def accept_data(self, device_id: UUID, data: dict):
        """ Получение данных от устройства с device_id и сохранение их в _data """
        logger.debug(f"Получены данные от устройства с индексом: {device_id}")
        self._data[device_id].append(data)

    def stop_recording(self, device_id: UUID):
        """ Остановка записи данных с устройства """
        if device_id not in self._data:
            logger.warning(f"Сохранение данных для устройства с индексом {device_id} уже установлено")

        try:
            self._save(device_id)
            logger.info(f"Данные для устройства с индексом {device_id} уже сохранены")
        except Exception as exc:
            logger.error(f"Ошибка сохранения данных для устройств с индексом {device_id}: {exc}")

    def _save(self, device_id: UUID):
        """ Сохранение данных для устройства с device_id """
        print(self._data[device_id])

