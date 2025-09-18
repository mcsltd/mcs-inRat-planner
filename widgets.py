import logging
from typing import Optional

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox, QDialogButtonBox

from structure import DataSchedule
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
            self.comboBoxExperiment.addItems(experiments)

        # fill combobox
        self.comboBoxExperiment.setEditable(True)
        self.comboBoxModelDevice.addItems(["InRat", "EMGsens"])
        self.comboBoxSamplingRate.addItems(["500 Гц", "1000 Гц", "2000 Гц"])
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

        # set text
        self.comboBoxExperiment.setCurrentText("Не выбрано")

        # set index
        self.comboBoxFormat.setCurrentIndex(1)
        self.comboBoxModelDevice.setCurrentIndex(1)
        self.comboBoxSamplingRate.setCurrentIndex(1)
        self.comboBoxDuration.setCurrentIndex(-1)
        self.comboBoxInterval.setCurrentIndex(-1)

        self.dateTimeEditStartExperiment.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditFinishExperiment.setDateTime(QDateTime.currentDateTime().addDays(1))

        self.dateTimeEditStartExperiment.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditFinishExperiment.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))


    def getSchedule(self) -> Optional[DataSchedule]:
        experiment = self.comboBoxExperiment.currentText()
        if experiment == "Не выбрано":
            # self.comboBoxExperiment.setFocus()
            return None

        patient = self.LineEditObject.text()
        if patient == "":
            # self.LineEditObject.setFocus()
            return None

        device_sn = self.LineEditSnDevice.text()
        if device_sn == "":
            # self.LineEditSnDevice.setFocus()
            return None

        device_model = self.comboBoxModelDevice.currentText()
        start_datetime = self.dateTimeEditStartExperiment.dateTime().toPython()
        finish_datetime = self.dateTimeEditStartExperiment.dateTime().toPython()

        interval = self.comboBoxInterval.currentText()
        if interval == "[hh:mm]":
            self.comboBoxInterval.setFocus()

        duration = self.comboBoxInterval.currentText()
        if duration == "[mm:ss]":
            self.comboBoxDuration.setFocus()

        file_format = self.comboBoxFormat.currentText()
        sampling_rate = self.comboBoxSamplingRate.currentText().split()[0]

        schd = DataSchedule(
            experiment=experiment,
            patient=patient,
            device_model=device_model, device_sn=device_sn,
            start_datetime=start_datetime, finish_datetime=finish_datetime,
            interval=interval, duration=duration,
            sampling_rate=sampling_rate, file_format=file_format
        )
        return schd

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
