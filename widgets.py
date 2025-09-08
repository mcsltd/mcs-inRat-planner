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

class DlgInputSchedule(Ui_DialogSchedule, QDialog):
    signal_insert = Signal()

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
        logger.debug("Add new task for {device_name}, {rat_name}, recording time: {recording_time} sec, repeat time: {recording_time} sec")


