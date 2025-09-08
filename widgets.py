import logging

from PyQt6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal

from ui.dlg_device import Ui_DlgDevice
from ui.dlg_rat import Ui_DlgRat
from ui.dlg_schedule import Ui_DialogSchedule

logger = logging.getLogger(__name__)


class DlgInputDevice(Ui_DlgDevice, QDialog):
    signal_insert = Signal(str, str, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Input Device")
        self.pushButton.clicked.connect(self.add)

    def add(self):
        name = self.lineEditNameDevice.text()
        serial = self.lineEditSerialDevice.text()
        model = self.lineEditModelDevice.text()
        logger.debug(f"Add new device: {name=} {serial=} {model=}")
        self.signal_insert.emit(name, serial, model)
        self.close()

class DlgInputRat(Ui_DlgRat, QDialog):
    signal_insert = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Input Rat")
        self.pushButtonAdd.clicked.connect(self.add)

    def add(self):
        name = self.lineEditNameRat.text()
        logger.debug(f"Add new animal: {name=}")
        self.signal_insert.emit(name)
        self.close()

from dataclasses import dataclass

@dataclass
class Task:
    device: dict
    rat: dict
    recording_duration: int
    repeat_time: int


class DlgInputSchedule(Ui_DialogSchedule, QDialog):
    signal_insert = Signal(Task)

    def __init__(
            self,
            devices: dict, rats: dict, # {"EMG-SENS-0000": UUID(...)} & {"Mikki": UUID(...)}
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # fill combobox for devices and rats
        self.fillComboBox(combobox=self.comboBoxRats, data=rats)
        self.fillComboBox(combobox=self.comboBoxDevices, data=devices)

        self.pushButtonCreateTask.clicked.connect(self.add)

    def fillComboBox(self, combobox: QComboBox, data: dict) -> None:
        for key in data.keys():
            combobox.addItem(key, data[key])

    def add(self) -> None:
        task = Task(
            device=self.comboBoxDevices.currentData(),
            rat=self.comboBoxRats.currentData(),
            recording_duration=int(self.lineEditRecordingDuration.text()),  # ToDo: add checkup
            repeat_time=int(self.lineEditRecordingRepeatTime.text()),       # ToDo: add checkup
        )

        logger.debug(f"Add new task for device {self.comboBoxDevices.currentText()} and rats {self.comboBoxDevices.currentText()}, task recording time: {task.recording_duration} sec, repeat time for task: {task.repeat_time} sec")
        self.signal_insert.emit(task)


