import ctypes


class InRatSettings(ctypes.Structure):
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

class InRatEvent(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Type", ctypes.c_uint8),
        ("Value", ctypes.c_uint8),
        ("Acceleration", Acceleration),
        ("Number", ctypes.c_uint32),
        ("Counter", ctypes.c_uint32),
        ("Data", ctypes.c_int32),
    ]

