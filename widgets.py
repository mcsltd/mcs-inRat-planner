import logging
from typing import Optional
from xml.dom import NoModificationAllowedErr

from PySide6.QtCore import QDateTime
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox, QDialogButtonBox, QPushButton, QMessageBox

from ui.v1.dlg_input_schedule import Ui_DlgCreateNewSchedule

logger = logging.getLogger(__name__)


class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):

    def __init__(self, experiments: Optional[list] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # setup datetime edit
        self.dateTimeEditStartExperiment.setCalendarPopup(True)
        self.dateTimeEditFinishExperiment.setCalendarPopup(True)

        if experiments is not None:
            self.ComboBoxExperiment.addItems(experiments)

        # fill combobox
        self.ComboBoxExperiment.setCurrentText("Не выбрано")
        self.ComboBoxExperiment.setEditable(True)
        self.ComboBoxModelDevice.addItems(["InRat", "EMGsens"])
        self.comboBoxFreq.addItems(["500 Гц", "1000 Гц", "2000 Гц"])
        self.comboBoxFormat.addItems(["Comma-separated values (CSV)", "European Data Format (EDF)", "Waveform Database (WFDB)"])
        self.comboBoxDuration.addItems(["01:00", "02:00", "03:00", "04:00", "05:00", "10:00", "15:00", "20:00"])
        self.comboBoxDuration.setPlaceholderText("[mm:ss]")
        self.comboBoxInterval.addItems(["01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "12:00", "24:00", "48:00"])
        self.comboBoxInterval.setPlaceholderText("[hh:mm]")

        # rename buttons
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Ok).setText("Ок")
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Cancel).setText("Отменить")
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.RestoreDefaults).setText("По умолчанию")

        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.setDefaults)

        self.setDefaults()


    def setDefaults(self):
        logger.info("Set default settings for schedule")

        self.comboBoxFormat.setCurrentIndex(1)
        # self.ComboBoxExperiment.setCurrentText("Не выбрано")
        self.ComboBoxModelDevice.setCurrentIndex(1)
        self.comboBoxFreq.setCurrentIndex(1)

        self.ComboBoxExperiment.setCurrentIndex(-1)
        self.comboBoxDuration.setCurrentIndex(-1)
        self.comboBoxInterval.setCurrentIndex(-1)

        self.dateTimeEditStartExperiment.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditFinishExperiment.setDateTime(QDateTime.currentDateTime().addDays(1))

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

        # return {
        #     "experiment": experiment, "object": patient,
        #     "device_sn": device_sn, "device_model": device_model,
        #     "duration": duration, "interval_repat": interval_repeat, "sampling_rate": sampling_rate, "format": save_format,
        #     "start_time": start_datetime_experiment, "finish_time": finish_datetime_experiment,
        # }
        return None

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
