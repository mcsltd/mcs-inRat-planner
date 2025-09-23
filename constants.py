import datetime
from typing import Any, Dict
from enum import Enum

DESCRIPTION_COLUMN_SCHEDULE = [
    "Эксперимент",
    "Объект",
    "SN \nрегистратора",
    "Модель \nрегистратора",
    "Дата начала\nэксперимента",
    "Статус",
    "Интервал \nповторения записи",
    "Длительность\n записи",
    "Общая \nдлительность",
    "Неудачных записей",
    "Всего \nзаписей",
    "Формат",
    "Частота"
]

EXAMPLE_DATA_SCHEDULE = [
    [
        "Эксперимент-X", "Mouse-1", "0001",
        "InRat", str(datetime.datetime.now().date()), "Идёт запись ЭКГ",
        "1 час", "30 минут", "3 часа", "0", "2", "EDF", "1000 Гц"
    ],
    [
        "Эксперимент-X", "Mouse-2", "0002",
        "InRat", str((datetime.datetime.now() + datetime.timedelta(hours=24)).date()), "До начала записи 1 день",
        "1 час", "10 минут", "0", "0", "0", "EDF", "500 Гц"
    ]
]

# old: ["№", "Имя объекта", "Серийный номер", "Частота", "Формат", "Длительность", "Интервал",]

DESCRIPTION_COLUMN_HISTORY = [
    "№",
    "Эксперимент",
    "Объект",
    "Дата записи",
    "Начало записи",
    "Конец записи",
    "Длительность",
    "Статус",
    "Формат"
]

EXAMPLE_DATA_HISTORY = [
    ["1", "Эксперимент-X", "Mouse-1", str(datetime.datetime.now().date()), datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(minutes=30), "30 минут", "Завершено", "EDF"],
    ["2", "Эксперимент-X", "Mouse-1", str(datetime.datetime.now().date()), datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(minutes=30), "30 минут", "Идёт запись", "WFDB"],
    ["3", "Эксперимент-X", "Mouse-1", str(datetime.datetime.now().date()), datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(minutes=30), "30 минут", "Завершено", "WFDB"],
]


class Formats(Enum):
    CSV = {"Comma Separate Value (CSV)": "CSV"}
    EDF = {"European Data Format (EDF)": "EDF"}
    WFDB = {"Waveform Database (WFDB)": "WFDB"}


class Devices(Enum):
    INRAT = {"InRat": "InRat-"}
    EMGSENS = {"EMGsens": "EMG-SENS-"}

