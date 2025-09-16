import logging
from typing import Optional
from xml.dom import NoModificationAllowedErr

from PySide6.QtCore import QDateTime
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox, QDialogButtonBox, QPushButton

from ui.v1.dlg_input_schedule import Ui_DlgCreateNewSchedule

logger = logging.getLogger(__name__)


class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # setup datetime edit
        self.dateTimeEditStartExperiment.setCalendarPopup(True)
        self.dateTimeEditFinishExperiment.setCalendarPopup(True)

        self.ComboBoxExperiment.setEditable(True)

        # setup combobox model device
        self.ComboBoxModelDevice.addItems(["InRat", "EMGsens"])
        # setup combobox sampling rate
        self.comboBoxFreq.addItems(["500 Гц", "1000 Гц", "2000 Гц"])
        # setup combobox saving format
        self.comboBoxFormat.addItems(
            ["Comma-separated values (CSV)", "European Data Format (EDF)", "Waveform Database (WFDB)"]
        )

        self.setDefaults()
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.setDefaults)

    def setDefaults(self):
        logger.info("Set default settings for schedule")

        self.comboBoxFormat.setCurrentIndex(1)
        self.ComboBoxExperiment.setCurrentText("Не выбрано")
        self.ComboBoxModelDevice.setCurrentIndex(1)
        self.comboBoxFreq.setCurrentIndex(1)

        self.dateTimeEditStartExperiment.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditFinishExperiment.setDateTime(QDateTime.currentDateTime().addMonths(1))

        self.dateTimeEditStartExperiment.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditFinishExperiment.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))


    def getSchedule(self) -> Optional[dict]:
        experiment = self.ComboBoxExperiment.currentText()
        patient = self.LineEditObject.text()
        device_sn = self.LineEditSnDevice.text()
        device_model = self.ComboBoxModelDevice.currentText()
        start_datetime_experiment = self.dateTimeEditStartExperiment.dateTime()
        finish_datetime_experiment = self.dateTimeEditStartExperiment.dateTime()
        save_format = self.comboBoxFormat.currentText()
        duration = None
        interval_repeat = None
        sampling_rate = self.comboBoxFreq.currentText().split()[0]

        # device_sn = self.lineEditSn.text()
        # sec_duration = self.convertTimeIntoSeconds(combobox=self.comboBoxDurationDim, spinbox=self.spinBoxDuration)
        # sec_interval = self.convertTimeIntoSeconds(combobox=self.comboBoxIntervalDim, spinbox=self.spinBoxInterval)

        return {
            "experiment": experiment, "object": patient,
            "device_sn": device_sn, "device_model": device_model,
            "duration": duration, "interval_repat": interval_repeat, "sampling_rate": sampling_rate, "format": save_format,
            "start_time": start_datetime_experiment, "finish_time": finish_datetime_experiment,
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
