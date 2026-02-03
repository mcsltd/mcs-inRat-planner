import datetime
import logging
import os
import numpy as np
import wfdb

from uuid import UUID

from PySide6.QtCore import QObject, Signal
from pyedflib import EdfWriter
from transliterate import detect_language, translit

from constants import Formats, RecordStatus
from structure import RecordingTaskData, RecordData
from config import SAVE_DIR

logger = logging.getLogger(__name__)

class Storage(QObject):

    signal_success_save = Signal(RecordData)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path_to_save = os.path.abspath(SAVE_DIR)

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

        if "signal" in data:
            signal = np.array(data["signal"])
            self._recording_task_data[device_id] = np.append(self._recording_task_data[device_id], signal)

    def stop_recording_task(self, device_id: UUID, acquisition_start_time: float) -> None:
        """ Остановка записи данных с устройства """
        if device_id not in self._devices_id:
            logger.warning(f"Отсутствует задача записи для {device_id}, данные не могут быть сохранены")
            return

        try:
            self._save(device_id, acquisition_start_time)
        except Exception as exc:
            logger.error(f"Ошибка сохранения данных для устройства с индексом {device_id}: {exc}")
        else:
            logger.info(f"Полученные данные для устройства с индексом {device_id} сохранены")
        finally:
            ...

    def _save(self, device_id: UUID, acquisition_start_time: float):
        """ Сохранение данных для устройства с device_id """
        record_property: RecordingTaskData = self._recording_task_property[device_id]

        device_name = record_property.device.ble_name
        obj_name = record_property.object.name
        experiment = record_property.experiment.name

        file_format = record_property.file_format
        sampling_rate = int(record_property.sampling_rate)

        signal = self.signal_truncation(
            signal=self._recording_task_data[device_id],
            sampling_rate=sampling_rate,
            seconds_duration=record_property.sec_duration
        )
        start_time = datetime.datetime.fromtimestamp(acquisition_start_time).replace(microsecond=0)

        write_dir = f"{self.path_to_save}\\{device_name}\\"
        filename = self.get_record_filename(experiment=experiment, obj_name=obj_name, start_time=start_time)

        path_to_file = None
        if file_format == list(Formats.EDF.value.values())[0]:
            # write_dir += r"EDF\"
            # create dir for saving files with selected format
            os.makedirs(write_dir, exist_ok=True)
            path_to_file = self._save_to_edf(
                filename=filename, write_dir=write_dir,
                sampling_rate=sampling_rate, ecg_signal=signal
            )

        elif file_format == list(Formats.WFDB.value.values())[0]:
            # write_dir += r"WFDB\"
            os.makedirs(write_dir, exist_ok=True)
            path_to_file = self._save_to_wfdb(
                filename=filename, write_dir=write_dir,
                sampling_rate=sampling_rate, start_time=start_time, ecg_signal=signal
            )

        if path_to_file is not None:
            task = self._recording_task_property[device_id]
            sec_duration = int(len(signal) / sampling_rate)

            record_data = task.get_result_record(
                start_time=start_time, duration=sec_duration, status=RecordStatus.OK, path=path_to_file)
            self.signal_success_save.emit(record_data)
        else:
            logger.error(f"Сигнал ЭКГ не записан в формат {record_property.file_format}")
            task = self._recording_task_property[device_id]
            record_data = task.get_result_record(start_time=start_time, duration=0, status=RecordStatus.ERROR)
            self.signal_success_save.emit(record_data)

        self._cleanup_task(device_id)

    def _save_to_edf(self, filename: str, write_dir: str, sampling_rate: int, ecg_signal: np.ndarray) -> str | None:
        logger.debug("Save data to edf.")

        file_name = None
        try:
            file_name = write_dir + f"{filename}.edf"

            writer = EdfWriter(
                n_channels=1, file_name=file_name,
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
                'label': "ECG", 'dimension': "uV", 'sample_frequency': sampling_rate,
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

    def _save_to_wfdb(
            self,
            filename: str,
            ecg_signal: np.ndarray, sampling_rate: int,
            write_dir: str, start_time, units: list[str] = ["uV"]) -> str | None:
        """ Сохранение данных в формате WFDB """
        path_to_save = None
        try:
            wfdb.io.wrsamp(
                record_name=filename,
                fs=sampling_rate, units=units, p_signal=ecg_signal[np.newaxis].T,
                sig_name=["ECG"], write_dir=write_dir, base_datetime=start_time,
            )
            logger.debug("Сигнал ЭКГ сохранен в WFDB формате")
            path_to_save = rf"{write_dir}\\{filename}"
        except Exception as exc:
            logger.error("Ошибка записи сигнала ЭКГ в формат WFDB")
        return path_to_save

    def _cleanup_task(self, device_id):
        self._devices_id.remove(device_id)
        del self._recording_task_data[device_id]
        del self._recording_task_property[device_id]

    def get_record_filename(self, experiment: str, obj_name: str, start_time: datetime.datetime) -> str:
        experiment = self.to_latin(experiment).replace(".", "_").replace(",", "_").replace(" ", "_")
        obj_name = self.to_latin(obj_name).replace(".", "_").replace(",", "_").replace(" ", "_")
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

    @staticmethod
    def signal_truncation(signal: np.ndarray, sampling_rate: int, seconds_duration: int) -> np.ndarray:
        trunc_signal = signal[:sampling_rate * seconds_duration]
        return trunc_signal