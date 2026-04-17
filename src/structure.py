import datetime
import uuid
from dataclasses import dataclass, field, asdict
from uuid import UUID

from constants import RecordStatus, Devices


@dataclass
class DeviceData:
    ble_name: str
    serial_number: int
    model: str
    id: UUID = field(default_factory=uuid.uuid4)

@dataclass
class ObjectData:
    name: str
    id: UUID = field(default_factory=uuid.uuid4)

@dataclass
class ExperimentData:
    name: str
    id: UUID = field(default_factory=uuid.uuid4)


@dataclass
class ScheduleData:
    experiment: ExperimentData | None
    device: DeviceData | None
    object: ObjectData | None
    sec_duration: int
    sec_interval: int
    datetime_start: datetime.datetime | None
    datetime_finish: datetime.datetime | None
    sampling_rate: int
    file_format: str
    id: UUID = field(default_factory=uuid.uuid4)

    def to_dict_with_ids(self) -> dict:
        """
        Преобразует объект в словарь, заменяя вложенные объекты на их ID.

        Returns:
            dict: Словарь с ID вместо объектов
        """
        result = {
            'id': self.id,
            'sec_duration': self.sec_duration,
            'sec_interval': self.sec_interval,
            'datetime_start': self.datetime_start,
            'datetime_finish': self.datetime_finish,
            'sampling_rate': self.sampling_rate,
            'file_format': self.file_format,
        }

        # обработка experiment
        if self.experiment:
            result['experiment_id'] = self.experiment.id if hasattr(self.experiment, 'id') else None
        else:
            raise ValueError("Поле experiment не заполнено")

        # обработка device
        if self.device:
            result['device_id'] = self.device.id if hasattr(self.device, 'id') else None
        else:
            raise ValueError("Поле device не заполнено")

        # обработка object
        if self.object:
            result['object_id'] = self.object.id if hasattr(self.object, 'id') else None
        else:
            raise ValueError("Поле object не заполнено")

        return result

@dataclass
class RecordData:
    datetime_start: datetime.datetime
    sec_duration: int
    file_format: str
    sampling_rate: int
    status: str
    schedule_id: UUID

    path: str | None = field(default=None)
    id: UUID = field(default_factory=uuid.uuid4)

@dataclass
class RecordingTaskData:
    """
    Класс, отвечающий за передачу BLEmanager задачи записи
    """
    schedule_id: UUID
    experiment: ExperimentData
    device: DeviceData
    object: ObjectData
    start_time: datetime.datetime

    sec_duration: int
    # finish_time: datetime.datetime

    file_format: str
    sampling_rate: int

    id: UUID = field(default_factory=uuid.uuid4)

    def get_result_record(self, start_time: datetime.datetime, duration: int, status: RecordStatus, path: str | None = None):
        """ Отдать результат выполнения задачи на запись сигнала """
        return RecordData(
            datetime_start=start_time, sec_duration=duration,
            file_format=self.file_format, sampling_rate=self.sampling_rate,
            status=status.value, schedule_id=self.schedule_id,
            path=path, id=self.id,
        )


if __name__ == "__main__":
    rd1 = RecordData(
        datetime_start=datetime.datetime.now(),
        sec_duration=10, file_format="csv", sampling_rate=1000, status=RecordStatus.IN_PROCESS.value,
        schedule_id=uuid.uuid4()
    )

    # rd2 = RecordData(
    #     datetime_start=datetime.datetime.now(),
    #     sec_duration=10, file_format="csv", sampling_rate=1000, status=RecordStatus.IN_PROCESS.value,
    #     schedule_id=uuid.uuid4()
    # )
    #
    # rd3 = RecordData(
    #     datetime_start=datetime.datetime.now(),
    #     sec_duration=10, file_format="csv", sampling_rate=1000, status=RecordStatus.IN_PROCESS.value,
    #     schedule_id=uuid.uuid4()
    # )
