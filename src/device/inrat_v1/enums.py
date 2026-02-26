from enum import IntEnum, IntFlag, auto


class Command(IntEnum):
    AcquisitionStart = 1
    AcquisitionStop = 2
    ConnectionClose = 3
    TurnOff = 4
    Activate = 5
    Deactivate = 6

class ScaleAccelerometer(IntEnum):
    G_2 = 0
    G_4 = 1
    G_8 = 2
    G_16 = 3

class SamplingRate(IntEnum):
    HZ_500 = 0
    HZ_1000 = 1
    HZ_2000 = 2

class EnabledChannels(IntFlag):
    ECG = 1

class EventType(IntFlag):
    BUTTON = 0
    ACTIVITY = auto()
    FREEFALL = auto()
    ORIENTATION = auto()
    START = auto()
    TEMP = auto()

