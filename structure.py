import datetime
import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class DeviceData:
    ble_name: str
    serial_number: int
    model: str
    id: UUID = uuid.uuid4()

@dataclass
class ObjectData:
    name: str
    id: UUID = uuid.uuid4()

@dataclass
class ExperimentData:
    name: str
    id: UUID = uuid.uuid4()


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
    id: UUID = uuid.uuid4()


