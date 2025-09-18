import datetime
from dataclasses import dataclass



@dataclass
class DataSchedule:
    experiment: str
    patient: str

    device_model: str
    device_sn: str

    start_datetime: datetime.datetime
    finish_datetime: datetime.datetime
    interval: str
    duration: str

    sampling_rate: int
    file_format: str