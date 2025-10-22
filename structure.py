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
    datetime_start: datetime.datetime
    datetime_finish: datetime.datetime
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

        # Обрабатываем experiment
        if self.experiment:
            result['experiment_id'] = self.experiment.id if hasattr(self.experiment, 'id') else None
        else:
            raise ValueError("Поле experiment не заполнено")

        # Обрабатываем device
        if self.device:
            result['device_id'] = self.device.id if hasattr(self.device, 'id') else None
        else:
            raise ValueError("Поле device не заполнено")

        # Обрабатываем object (object - зарезервированное слово, поэтому используем object_id)
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
    id: UUID = field(default_factory=uuid.uuid4)



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
