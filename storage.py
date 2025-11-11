import logging
import os
import numpy as np

from uuid import UUID

from PySide6.QtCore import QObject, Signal
from pyedflib import EdfWriter


from constants import Formats, RecordStatus
from structure import RecordingTaskData, RecordData

logger = logging.getLogger(__name__)

class Storage(QObject):

    signal_success_save = Signal(RecordData)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._devices_id: set[UUID] = set()
        self._recording_task_data: dict[UUID, np.ndarray] = {}
        self._recording_task_property: dict[UUID, RecordingTaskData] = {}


    def add_recording_task(self, task: RecordingTaskData) -> None:
        """ Начало записи данных, приходящих из BleManager """
        if task.device.id in self._devices_id:
            logging.warning(f"Для устройства c индексом {task.device.id} уже создана задача на запись")
            return

        logger.info(f"Начало записи данных для устройства с индексом {task.device.id}")
        self._devices_id.add(task.device.id)
        self._recording_task_data[task.device.id] = np.array([])
        self._recording_task_property[task.device.id] = task

    def accept_data(self, device_id: UUID, data: dict) -> None:
        """ Получение данных от устройства с device_id и сохранение их в _data """
        logger.debug(f"Получены данные от устройства с индексом: {device_id}")
        signal = np.array(data["emg"])
        self._recording_task_data[device_id] = np.append(self._recording_task_data[device_id], signal)

    def stop_recording_task(self, device_id: UUID) -> None:
        """ Остановка записи данных с устройства """
        if device_id not in self._devices_id:
            logger.warning(f"Отсутствует задача записи для {device_id}, данные не могут быть сохранены")
            return

        try:
            self._save(device_id)
        except Exception as exc:
            logger.error(f"Ошибка сохранения данных для устройства с индексом {device_id}: {exc}")
        else:
            logger.info(f"Полученные данные для устройства с индексом {device_id} сохранены")
        finally:
            ...

    def _save(self, device_id: UUID):
        """ Сохранение данных для устройства с device_id """
        record_property: RecordingTaskData = self._recording_task_property[device_id]
        record_id = record_property.id
        device_name = record_property.device.ble_name
        file_format = record_property.file_format
        sampling_rate = int(record_property.sampling_rate)
        signal = self._recording_task_data[device_id]

        write_dir = f".\\data\\{device_name}\\"

        path_to_file = None
        if file_format == list(Formats.EDF.value.values())[0]:
            write_dir += "EDF\\"
            # create dir for saving files with selected format
            os.makedirs(write_dir, exist_ok=True)
            path_to_file = self.save_to_edf(record_id, write_dir, sampling_rate, signal)

        if path_to_file is not None:
            task = self._recording_task_property[device_id]
            sec_duration = (task.finish_time - task.start_time).seconds

            record_data = task.get_result_record(duration=sec_duration, status=RecordStatus.OK, path=path_to_file)
            self.signal_success_save.emit(record_data)
        else:
            ...
        self._cleanup_task(device_id)


    def save_to_edf(self, record_id: UUID, write_dir: str, sampling_rage: int, ecg_signal: np.ndarray) -> str | None:
        logger.debug("Save data to edf.")

        file_name = None
        try:
            file_name = write_dir + f"{record_id}.edf"

            writer = EdfWriter(
                n_channels=1,
                file_name=file_name,
            )

            self.signal = np.round(ecg_signal * 1e6, decimals=3)

            margin = 0.15
            signal_max = np.max(self.signal)
            signal_min = np.min(self.signal)
            physical_max = np.round(signal_max * (1 + margin) if signal_max > 0 else signal_max * (1 - margin),
                                    decimals=3)
            physical_min = np.round(signal_min * (1 - margin) if signal_min > 0 else signal_min * (1 + margin),
                                    decimals=3)

            channel_info = {
                'label': "ECG", 'dimension': "uV", 'sample_frequency': sampling_rage,
                'physical_max': physical_max, 'physical_min': physical_min,
                'digital_max': 32767, 'digital_min': -32768,
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

    def _cleanup_task(self, device_id):

        self._devices_id.remove(device_id)
        del self._recording_task_data[device_id]
        del self._recording_task_property[device_id]