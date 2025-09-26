import datetime
from dataclasses import dataclass

@dataclass
class DataSchedule:
    experiment: str     # Optional field
    patient: str        # Optional field

    device_model: str # -> "EMG-SENS-{device_sn}" or "inRat"
    device_sn: str

    start_datetime: datetime.datetime
    finish_datetime: datetime.datetime
    sec_interval: int
    sec_duration: int

    sampling_rate: int
    file_format: str


