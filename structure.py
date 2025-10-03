import datetime
import uuid
from dataclasses import dataclass, field
from uuid import UUID

from constants import RecordStatus


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

@dataclass
class RecordData:
    datetime_start: datetime.datetime
    sec_duration: int
    file_format: str
    sampling_rate: int
    status: RecordStatus
    schedule_id: UUID
    id: UUID = field(default_factory=uuid.uuid4)


if __name__ == "__main__":
    rd1 = RecordData(
        datetime_start=datetime.datetime.now(),
        sec_duration=10, file_format="csv", sampling_rate=1000, status=RecordStatus.IN_PROCESS,
        schedule_id=uuid.uuid4()
    )

    rd2 = RecordData(
        datetime_start=datetime.datetime.now(),
        sec_duration=10, file_format="csv", sampling_rate=1000, status=RecordStatus.IN_PROCESS,
        schedule_id=uuid.uuid4()
    )

    rd3 = RecordData(
        datetime_start=datetime.datetime.now(),
        sec_duration=10, file_format="csv", sampling_rate=1000, status=RecordStatus.IN_PROCESS,
        schedule_id=uuid.uuid4()
    )
