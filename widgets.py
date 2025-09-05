import logging

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal

from ui.dlg_device import Ui_DlgDevice
from ui.dlg_rat import Ui_DlgRat


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
