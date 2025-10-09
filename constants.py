import datetime
from typing import Any, Dict
from enum import Enum

DESCRIPTION_COLUMN_SCHEDULE = [
    "id",
    "Эксперимент",
    "Дата начала",
    "Дата окончания",
    "Объект",
    "Устройство",
    "Статус",
    "Периодичность\nзаписи",
    "Длительность\nзаписи",
    "Общая\nдлительность",
    "Всего\nзаписей",
    "Ошибок\nзаписи",
    "Параметры записи"
]

EXAMPLE_DATA_SCHEDULE = [
    [
        "Эксперимент-X", str(datetime.datetime.now().replace(microsecond=0)),
        str(datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=10)), "Mouse-1", "InRat-0001", "Идёт запись ЭКГ",
        "1 час", "30 минут", "3 часа", "0", "2", "EDF; 1000 Гц"
    ],
    [
        "Эксперимент-X", str(datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=24)),
        str(datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=10)), "Mouse-2", "InRat-0002",
        "До начала записи 1 день", "1 час", "10 минут", "0", "0", "0", "EDF; 500 Гц"
    ]
]

# old: ["№", "Имя объекта", "Серийный номер", "Частота", "Формат", "Длительность", "Интервал",]

DESCRIPTION_COLUMN_HISTORY = [
    "id",
    "№",
    "Начало записи",
    "Длительность",
    "Эксперимент",
    "Объект",
    "Формат"
]

EXAMPLE_DATA_HISTORY = [
    ["1", str(datetime.datetime.now().replace(microsecond=0)), "30 минут", "Эксперимент-X", "Mouse-1", "EDF"],
    ["2", str(datetime.datetime.now().replace(microsecond=0)), "30 минут", "Эксперимент-X", "Mouse-1", "WFDB"],
    ["3", str(datetime.datetime.now().replace(microsecond=0)), "30 минут", "Эксперимент-X", "Mouse-1", "WFDB"],
]


class Formats(Enum):
    CSV = {"Comma Separate Value (CSV)": "CSV"}
    EDF = {"European Data Format (EDF)": "EDF"}
    WFDB = {"Waveform Database (WFDB)": "WFDB"}


class Devices(Enum):
    INRAT = {"InRat": "InRat-"}
    EMGSENS = {"EMGsens": "EMG-SENS-"}

class RecordStatus(Enum):
    ERROR = "Error" # ошибка записи
    IN_PROCESS = "Recording"
    OK = "Ok"