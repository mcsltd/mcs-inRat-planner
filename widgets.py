import logging
from enum import Enum
from typing import Optional

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox, QDialogButtonBox, QMessageBox

from constants import Formats, Devices
from structure import DataSchedule
from ui.v1.dlg_input_schedule import Ui_DlgCreateNewSchedule
from ui.v1.dlg_input_experiment import Ui_DlgInputExperiment

logger = logging.getLogger(__name__)


class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):

    def __init__(self, experiments: Optional[list | set] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.has_unsaved_changes = False

        # setup datetime edit
        self.dateTimeEditStartExperiment.setCalendarPopup(True)
        self.dateTimeEditFinishExperiment.setCalendarPopup(True)

        self.comboBoxExperiment.setPlaceholderText("Не выбрано")
        if experiments is not None:
            # self.comboBoxExperiment.addItems(experiments)
            for exp_id, exp in experiments:
                self.comboBoxExperiment.addItem(exp , userData=exp_id)

            self.comboBoxExperiment.setCurrentIndex(-1)

        # fill combobox
        # self.comboBoxExperiment.setEditable(True)
        self.fill_combobox(self.comboBoxModelDevice, Devices)
        self.comboBoxSamplingRate.addItems(["500 Гц", "1000 Гц", "2000 Гц"])
        self.fill_combobox(self.comboBoxFormat, Formats)

        self.comboBoxDuration.setPlaceholderText("[mm:ss]")
        self.comboBoxDuration.addItems(["01:00", "02:00", "03:00", "04:00", "05:00", "10:00", "15:00", "20:00"])

        self.comboBoxInterval.setPlaceholderText("[hh:mm]")
        self.comboBoxInterval.addItems(["01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "12:00", "24:00", "48:00"])

        # rename buttons
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Ok).setText("Ок")
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Cancel).setText("Отменить")
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.RestoreDefaults).setText("По умолчанию")

        # monitoring the has_unsaved_change flag
        self.comboBoxExperiment.editTextChanged.connect(self.on_form_changed)
        self.LineEditObject.textChanged.connect(self.on_form_changed)
        self.LineEditSnDevice.textChanged.connect(self.on_form_changed)

        # self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.setDefaults)

        self.setDefaults()

    @staticmethod
    def fill_combobox(combobox: QComboBox, enumeration: Enum) -> None:
        for field in enumeration:
            combobox.addItem(list(field.value.keys())[0], userData=field)


    def on_form_changed(self) -> None:
        if self.has_unsaved_changes:
            return

        if self.comboBoxExperiment.currentText() != "Не выбрано":
            self.has_unsaved_changes = True
            logger.debug("Detected unsaved change...")

        if self.LineEditSnDevice.text() != "" or self.LineEditObject.text() != "":
            self.has_unsaved_changes = True
            logger.debug("Detected unsaved change...")


    def closeEvent(self, event):
        logger.info("Close dialog window")

        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self,"Подтверждение выхода",
                "У вас есть несохраненные изменения. Вы уверены, что хотите выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        event.accept()

    def setDefaults(self):
        logger.info("Set default settings for schedule")
        self.has_unsaved_changes = False

        # set text
        self.comboBoxExperiment.setPlaceholderText("Не выбрано")
        self.LineEditSnDevice.setText("")
        self.LineEditObject.setText("")

        # set index
        self.comboBoxExperiment.setCurrentIndex(-1)
        self.comboBoxFormat.setCurrentIndex(1)
        self.comboBoxModelDevice.setCurrentIndex(1)
        self.comboBoxSamplingRate.setCurrentIndex(1)
        self.comboBoxDuration.setCurrentIndex(-1)
        self.comboBoxInterval.setCurrentIndex(-1)

        # ToDo: start_time < finish_time
        self.dateTimeEditStartExperiment.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditFinishExperiment.setMinimumDateTime(QDateTime.currentDateTime().addDays(2).addSecs(60))


    def getSchedule(self) -> Optional[DataSchedule]:
        experiment_id = self.comboBoxExperiment.currentData()
        experiment = self.comboBoxExperiment.currentText()

        patient = self.LineEditObject.text()


        device_sn = self.LineEditSnDevice.text()
        device_model = f"{list(self.comboBoxModelDevice.currentData().value.values())[0]}{device_sn}"

        start_datetime = self.dateTimeEditStartExperiment.dateTime().toPython().replace(microsecond=0)
        finish_datetime = self.dateTimeEditStartExperiment.dateTime().toPython().replace(microsecond=0)

        sec_interval = self.convert_to_seconds(self.comboBoxInterval.currentText(), time_format="[hh:mm]")
        sec_duration = self.convert_to_seconds(self.comboBoxDuration.currentText(), time_format="[mm:ss]")

        file_format = list(self.comboBoxFormat.currentData().value.values())[0]
        sampling_rate = self.comboBoxSamplingRate.currentText().split()[0]

        schd = DataSchedule(
            experiment_id=experiment_id,
            experiment=experiment,
            patient=patient,
            device_model=device_model, device_sn=device_sn,
            start_datetime=start_datetime, finish_datetime=finish_datetime,
            sec_interval=sec_interval, sec_duration=sec_duration,
            sampling_rate=sampling_rate, file_format=file_format
        )

        return schd

    def convert_to_seconds(self, duration: str, time_format: str) -> int:
        sec_duration = 0

        if time_format == "[mm:ss]":    # duration
            duration = "0:" + duration
        if time_format == "[hh:mm]":    # interval
            duration = duration + "0:"

        time = duration.replace(":", " ").split()[::-1]
        for i, t in enumerate(time):
            sec_duration += int(t) * (60 ** i)
        return sec_duration

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


class DlgCreateExperiment(Ui_DlgInputExperiment, QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

    def getExperiment(self):
        return self.lineEditExperiment.text()