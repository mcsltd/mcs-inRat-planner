import logging
from typing import Optional

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox

from ui.v1.dlg_input_schedule import Ui_DlgCreateNewSchedule

logger = logging.getLogger(__name__)


class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # setup QDateTimeEdit
        self.dateTimeEditStartRecord.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditStartRecord.setCalendarPopup(True)

        # set default value for ComboBox
        self.comboBoxFreq.setCurrentIndex(1)            # default 1000 Hz
        self.comboBoxIntervalDim.setCurrentIndex(1)

        # set default value for QLineEdit
        self.spinBoxDuration.setValue(30)
        self.spinBoxInterval.setValue(1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getSchedule(self) -> Optional[dict]:

        patient = self.lineEditObj.text()
        device_sn = self.lineEditSn.text()

        sec_duration = self.convertTimeIntoSeconds(combobox=self.comboBoxDurationDim, spinbox=self.spinBoxDuration)
        sec_interval = self.convertTimeIntoSeconds(combobox=self.comboBoxIntervalDim, spinbox=self.spinBoxInterval)

        starttime = self.dateTimeEditStartRecord.dateTime()
        format = self.comboBoxFormat.currentText()
        freq = self.comboBoxFreq.currentText()

        return {
            "patient_name": patient,
            "device_sn": device_sn,
            "duration": sec_duration,
            "interval": sec_interval,
            "start_time": starttime,
            "format": format,
            "freq": freq
        }

    @classmethod
    def convertTimeIntoSeconds(cls, combobox: QComboBox, spinbox: QSpinBox) -> int:
        crnt_unit = combobox.currentText()
        if crnt_unit == "секунд":
            return spinbox.value()
        elif crnt_unit == "минут":
            return spinbox.value() * 60
        elif crnt_unit == "часов":
            return spinbox.value() * (60 ** 2)
        raise ValueError("Invalid data type")
