import logging
import uuid
from enum import Enum
from typing import Optional

from PySide6.QtCore import QDateTime, Signal, QDate, QTime
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox, QDialogButtonBox, QMessageBox

from constants import Formats, Devices
from db.database import connection
from db.models import Experiment
from db.queries import get_experiments
from structure import ExperimentData, ObjectData, DeviceData, ScheduleData

from ui.v1.dlg_input_schedule import Ui_DlgCreateNewSchedule
from ui.v1.dlg_input_experiment import Ui_DlgInputExperiment

logger = logging.getLogger(__name__)


class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):

    signal_add_experiment = Signal()

    def __init__(self, schedule: Optional[ScheduleData | set] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.default_schedule: ScheduleData = schedule
        self.has_unsaved_changes = False

        if schedule is not None:
            self.setWindowTitle("Изменение расписания")

        # setup datetime edit
        self.dateTimeEditStartExperiment.setCalendarPopup(True)
        self.dateTimeEditFinishExperiment.setCalendarPopup(True)

        self.comboBoxExperiment.setPlaceholderText("Не выбрано")
        self.fill_combobox_experiment()

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

        self.setDefaults()

        # monitoring the has_unsaved_change flag
        self.comboBoxExperiment.editTextChanged.connect(self.on_form_changed)
        self.LineEditObject.textChanged.connect(self.on_form_changed)
        self.LineEditSnDevice.textChanged.connect(self.on_form_changed)

        # соединение кнопок с методами
        # self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self.buttonBoxSchedule.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.setDefaults)
        self.pushButtonAddExperiment.clicked.connect(self.add_experiment)

    def _upload(self, schedule: ScheduleData):
        """ Загрузка данных расписания """
        # experiment
        self.set_combobox_value(self.comboBoxExperiment, schedule.experiment.name)

        # object
        self.LineEditObject.setText(schedule.object.name)

        # model
        models = {"EMG-SENS-": "EMGsens", "InRat-": "InRat"}
        self.set_combobox_value(self.comboBoxModelDevice, models[schedule.device.model])

        # serial number
        self.LineEditSnDevice.setText(str(schedule.device.serial_number))

        # schedule
        # start time
        st = schedule.datetime_start
        self.dateTimeEditStartExperiment.setDateTime(
            QDateTime(QDate(st.year, st.month, st.day), QTime(st.hour, st.minute, st.second))
        )

        # finish time
        ft = schedule.datetime_finish
        self.dateTimeEditFinishExperiment.setDateTime(
            QDateTime(QDate(ft.year, ft.month, ft.day), QTime(ft.hour, ft.minute, ft.second))
        )
        # interval
        interval = self.convert_seconds_to_combobox_data(seconds=schedule.sec_interval, time_format="[hh:mm]")
        self.set_combobox_value(self.comboBoxInterval, interval)

        # param records
        # record duration
        duration = self.convert_seconds_to_combobox_data(seconds=schedule.sec_duration, time_format="[mm:ss]")
        self.set_combobox_value(self.comboBoxDuration, duration)

        # sampling rate
        self.set_combobox_value(self.comboBoxSamplingRate, f"{schedule.sampling_rate} Гц")

        # file format
        formats = {
            "CSV" : "Comma Separate Value (CSV)",
            "EDF" : "European Data Format (EDF)",
            "WFDB" : "Waveform Database (WFDB)"
        }
        self.set_combobox_value(self.comboBoxFormat, formats[schedule.file_format])

    def set_combobox_value(self, combobox: QComboBox, value: str) -> None:
        idx = combobox.findText(value)
        if idx == -1:
            raise ValueError(f"Не найдено значение: {idx=}")
        combobox.setCurrentIndex(idx)

    def fill_combobox_experiment(self):
        exps = get_experiments()
        if exps is not None:
            for exp_id, exp in exps:
                self.comboBoxExperiment.addItem(exp, userData=exp_id)
            self.comboBoxExperiment.setCurrentIndex(-1)

    @connection
    def add_experiment(self, session) -> None:
        dlg = DlgCreateExperiment()
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            exp = dlg.getExperiment()
            experiment_id = Experiment.from_dataclass(exp).create(session)
            logger.info(f"Add Experiment in DB: id={experiment_id}")

            # add experiment in db
            self.comboBoxExperiment.addItem(exp.name, exp.id)
            self.comboBoxExperiment.setCurrentIndex(0)
        return

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
        self.has_unsaved_changes = False

        if self.default_schedule is not None:
            logger.debug(f"Установка настроек по умолчанию из структуры расписания: {self.default_schedule}")
            self._upload(self.default_schedule)
            return

        logger.info("Установка настроек по умолчанию")

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


    def getSchedule(self) -> Optional[ScheduleData]:
        # experiment
        experiment_id = self.comboBoxExperiment.currentData()
        experiment = self.comboBoxExperiment.currentText()
        exp_d: ExperimentData = ExperimentData(id=experiment_id, name=experiment)

        if experiment_id is None:
            reply = QMessageBox.question(
                self, "Пустое поле `Эксперимент`",
                "Ошибка создания расписания",
                QMessageBox.StandardButton.Ok
            )
            return None

        # object
        if self.default_schedule is None:
            object_id = uuid.uuid4()
        else:
            object_id = self.default_schedule.object.id

        obj = self.LineEditObject.text()
        obj_d: ObjectData = ObjectData(id=object_id, name=obj)

        # device
        if self.default_schedule is None:
            device_id = uuid.uuid4()
        else:
            device_id = self.default_schedule.device.id

        device_sn = self.LineEditSnDevice.text()
        device_model = f"{list(self.comboBoxModelDevice.currentData().value.values())[0]}"
        dev_d: DeviceData = DeviceData(id=device_id, ble_name=f"{device_model}{device_sn}", model=device_model, serial_number=device_sn)

        start_datetime = self.dateTimeEditStartExperiment.dateTime().toPython().replace(microsecond=0)
        finish_datetime = self.dateTimeEditFinishExperiment.dateTime().toPython().replace(microsecond=0)
        sec_interval = self.convert_to_seconds(self.comboBoxInterval.currentText(), time_format="[hh:mm]")
        sec_duration = self.convert_to_seconds(self.comboBoxDuration.currentText(), time_format="[mm:ss]")
        file_format = list(self.comboBoxFormat.currentData().value.values())[0]
        sampling_rate = self.comboBoxSamplingRate.currentText().split()[0]

        if self.default_schedule is None:
            schedule_id = uuid.uuid4()
        else:
            schedule_id = self.default_schedule.id

        # schedule
        sch_d = ScheduleData(
            id=schedule_id,
            experiment=exp_d,
            device=dev_d,
            object=obj_d,
            datetime_start=start_datetime, datetime_finish=finish_datetime,
            sec_interval=sec_interval, sec_duration=sec_duration,
            sampling_rate=sampling_rate, file_format=file_format
        )

        return sch_d

    def convert_to_seconds(self, duration: str, time_format: str) -> int:
        sec_duration = 0

        if time_format == "[mm:ss]":    # duration
            duration = "0:" + duration
        if time_format == "[hh:mm]":    # interval
            duration = duration + ":0"

        time = duration.replace(":", " ").split()[::-1]
        for i, t in enumerate(time):
            sec_duration += int(t) * (60 ** i)
        return sec_duration

    def convert_seconds_to_combobox_data(self, seconds: int, time_format: str) -> str | None:
        if time_format == "[mm:ss]":    # duration
            s = seconds % 60
            m = seconds // 60
            return f"{m:02d}:{s:02d}"
        if time_format == "[hh:mm]":    # interval
            m = seconds // 60 % 60
            h = seconds // 3600
            return f"{h:02d}:{m:02d}"
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


class DlgCreateExperiment(Ui_DlgInputExperiment, QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

    def getExperiment(self) -> ExperimentData:
        exp_d = ExperimentData(name=self.lineEditExperiment.text())
        return exp_d