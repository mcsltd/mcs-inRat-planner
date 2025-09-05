import ctypes
from enum import IntFlag, auto


class BatteryProperties(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Capacity", ctypes.c_uint16),
        ("Level", ctypes.c_uint16),
        ("Voltage", ctypes.c_uint16),
        ("Current", ctypes.c_int16),
        ("Temperature", ctypes.c_int16)
    ]


class Settings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("DataRateEMG", ctypes.c_uint8),
        ("AveragingWindowEMG", ctypes.c_uint8),
        ("FullScaleAccelerometer", ctypes.c_uint8),
        ("FullScaleGyroscope", ctypes.c_uint8),
        ("EnabledChannels", ctypes.c_uint8),
        ("EnabledEvents", ctypes.c_uint16),
        ("ActivityThreshold", ctypes.c_uint16),
    ]



class AngularRate(ctypes.Structure):
    _fields_ = [
        ("P", ctypes.c_int16),
        ("R", ctypes.c_int16),
        ("Y", ctypes.c_int16),
    ]


class Acceleration(ctypes.Structure):
    _fields_ = [
        ("X", ctypes.c_int16),
        ("Y", ctypes.c_int16),
        ("Z", ctypes.c_int16)
    ]


class Event(ctypes.Structure):
    _pack_ = 1 # remove offset
    _fields_ = [
        ("Type", ctypes.c_uint8),
        ("Value", ctypes.c_uint8),
        ("Acceleration", Acceleration),
        ("AngularRate", AngularRate),
        ("Number", ctypes.c_uint32),
        ("Counter", ctypes.c_uint32),
    ]


class RGB(ctypes.Structure):
    _fields_ = [
        ("R", ctypes.c_uint8),
        ("G", ctypes.c_uint8),
        ("B", ctypes.c_uint8),
    ]


