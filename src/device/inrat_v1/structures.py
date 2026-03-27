import ctypes
from dataclasses import dataclass


# классы данных
@dataclass
class UsageData:
    power_on_count: int
    advertising_seconds: int
    connection_seconds: int
    data_send_seconds: int

    def __str__(self):
        return (f"Использование: PowerOnCount={self.power_on_count}; AdvertisingSeconds={self.advertising_seconds}; "
                f"ConnectionSeconds={self.connection_seconds}; DataSendSeconds={self.data_send_seconds}")

@dataclass
class StatusData:
    activated: bool
    vddio: int
    usage: UsageData

    def __str__(self):
        return f"Статус: Activated={self.activated}; Vddio={self.vddio}; {str(self.usage)}"


# структуры
class Settings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("DataRateEcg", ctypes.c_uint8),
        ("HighPassFilterEcg", ctypes.c_uint8),
        ("FullScaleAccelerometer", ctypes.c_uint8),
        ("EnabledChannels", ctypes.c_uint8),
        ("EnabledEvents", ctypes.c_uint16),
        ("ActivityThreshold", ctypes.c_uint16),
    ]


class Acceleration(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("X", ctypes.c_int16),
        ("Y", ctypes.c_int16),
        ("Z", ctypes.c_int16)
    ]

class Event(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Type", ctypes.c_uint8),
        ("Value", ctypes.c_uint8),
        ("Acceleration", Acceleration),
        ("Number", ctypes.c_uint32),
        ("Counter", ctypes.c_uint32),
        ("Data", ctypes.c_int32),
    ]


class Usage(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("PowerOnCount", ctypes.c_uint32),
        ("AdvertisingSeconds", ctypes.c_uint32),
        ("ConnectionSeconds", ctypes.c_uint32),
        ("DataSendSeconds", ctypes.c_uint32)
    ]

class Status(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Activated", ctypes.c_uint16),
        ("Vddio", ctypes.c_uint16),
        ("Usage", Usage)
    ]
    def to_dataclass(self) -> StatusData:
        return StatusData(
            activated= self.Activated == 1,
            vddio=self.Vddio,
            usage = UsageData(
                power_on_count=self.Usage.PowerOnCount,
                advertising_seconds=self.Usage.AdvertisingSeconds,
                connection_seconds=self.Usage.ConnectionSeconds,
                data_send_seconds=self.Usage.DataSendSeconds
              )
        )