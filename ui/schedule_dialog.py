import datetime
import logging
import uuid
from enum import Enum
from typing import Optional

from PySide6.QtCore import QDateTime, Signal, QDate, QTime, QTimer
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import QDialog, QComboBox, QSpinBox, QDialogButtonBox, QMessageBox, QWidget

from constants import Formats, Devices
from db.database import connection
from db.models import Experiment
from db.queries import get_experiments
from structure import ExperimentData, ObjectData, DeviceData, ScheduleData

from resources.v1.dlg_input_schedule__new import Ui_DlgCreateNewSchedule
from resources.v1.dlg_input_experiment import Ui_DlgInputExperiment
PATH_TO_ICON = "resources/v1/icon_app.svg"

logger = logging.getLogger(__name__)

class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):
    signal_add_experiment = Signal()
    def __init__(self, schedule: Optional[ScheduleData | set] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))
        self.setFixedSize(self.size())

        self.default_schedule: ScheduleData = schedule
        self.has_unsaved_changes = False

        if schedule is not None:
            self.setWindowTitle("Изменение расписания")

        # настройка поля ввода серийного номера
        validator = QIntValidator(0, 9999, self)
        self.LineEditSnDevice.setMaxLength(4)
        self.LineEditSnDevice.setValidator(validator)

        # setup datetime edit
        self.dateTimeEditStartExperiment.setCalendarPopup(True)
        self.dateTimeEditFinishExperiment.setCalendarPopup(True)

        self.comboBoxExperiment.setPlaceholderText("Не выбрано")
        self.fill_combobox_experiment()

        self.fill_combobox(self.comboBoxModelDevice, Devices)
        self.comboBoxSamplingRate.addItems(["1000 Гц", "2000 Гц", "5000 Гц"])
        self.fill_combobox(self.comboBoxFormat, Formats)

        self.comboBoxDuration.addItems(
            ["1 минута", "2 минуты", "3 минуты", "4 минуты", "5 минут", "10 минут", "15 минут", "20 минут"])

        # self.comboBoxInterval.setPlaceholderText("[hh:mm]")
        self.comboBoxInterval.addItems(["10 минут", "20 минут", "30 минут", "1 час", "2 часа", "3 часа"])

        # rename buttons
        self.setDefaults()

        # monitoring the has_unsaved_change flag
        self.comboBoxExperiment.editTextChanged.connect(self.on_form_changed)
        self.LineEditObject.textChanged.connect(self.on_form_changed)
        self.LineEditSnDevice.textChanged.connect(self.on_form_changed)
        self.dateTimeEditStartExperiment.dateTimeChanged.connect(self.on_start_datetime_changed)

        self.pushButtonByDefault.clicked.connect(self.setDefaults)
        self.pushButtonOk.clicked.connect(self.on_ok_clicked)
        self.pushButtonCancel.clicked.connect(self.close)

        self.pushButtonAddExperiment.clicked.connect(self.add_experiment)

        if schedule is None:
            self.timer_update = QTimer()
            self.timer_update.setInterval(1000)
            self.timer_update.timeout.connect(self._update_time_edit)
            self.timer_update.start()

    def on_start_datetime_changed(self):
        """ Обработка изменения даты со временем в окне ввода времени """
        # обработка ошибки finish_time < start_time, finish_time всегда должен быть больше или равен start_time
        start_time = self.dateTimeEditStartExperiment.dateTime()
        self.dateTimeEditFinishExperiment.setMinimumDateTime(start_time)

    def _update_time_edit(self):
        """ Установить в dateTimeEditStartExperiment время больше текущего времени на 1 минуту"""
        current_time = datetime.datetime.now().replace(second=0, microsecond=0)
        start_time = self.dateTimeEditStartExperiment.dateTime().toPython().replace(second=0, microsecond=0)

        if current_time >= start_time:
            start_time += datetime.timedelta(minutes=1)
            self.dateTimeEditStartExperiment.setDateTime(
                QDateTime(
                    QDate(start_time.year, start_time.month, start_time.day),
                    QTime(start_time.hour, start_time.minute, start_time.second))
            )
            logger.info(f"Изменено время начала записи ЭКГ: {str(start_time)}")

    def on_ok_clicked(self):
        """ Обработчик нажатия кнопки Ok """
        if not self.validate_input():   # проверка если обязательные поля не были заполнены
            return

        self.accept()

    def validate_input(self) -> bool:
        """ Проверка заполнения обязательных полей """
        errors = []

        # проверка данных эксперимента
        if self.comboBoxExperiment.currentIndex() == -1:    # не выбрано
            logger.warning("Не выбрано название эксперимента в списке")
            self.highlight_field(self.comboBoxExperiment)
            errors.append("Необходимо выбрать значение в списке \"Эксперимент\"")
        else:
            self.clear_highlight(self.comboBoxExperiment)

        # проверка данных объекта
        if not self.LineEditObject.text().strip():
            logger.warning("Не введено название объекта в поле ввода")
            self.highlight_field(self.LineEditObject)
            errors.append("Поле \"Объект\" обязательно для заполнения")
        else:
            self.clear_highlight(self.LineEditObject)

        # проверка серийного номера
        if not self.LineEditSnDevice.text().strip():
            logger.warning("Не введено значение серийного номера в поле ввода")
            self.highlight_field(self.LineEditSnDevice)
            errors.append("Поле \"Серийный номер устройства\" обязательно для заполнения")
        elif len(self.LineEditSnDevice.text().strip()) < 4:
            logger.warning("Введено неправильное значение серийного номера в поле ввода")
            self.highlight_field(self.LineEditSnDevice)
            errors.append("В поле \"Серийный номер устройства\" должно быть введено 4 числа")
        else:
            self.clear_highlight(self.LineEditSnDevice)

        # проверка времени старта и конца расписания
        st = self.dateTimeEditFinishExperiment.dateTime().toPython()
        ft = self.dateTimeEditStartExperiment.dateTime().toPython()
        if st == ft:
            logger.warning("Время старта равно времени конца записи")
            self.highlight_field(self.dateTimeEditStartExperiment)
            self.highlight_field(self.dateTimeEditFinishExperiment)
            errors.append("\"Дата начала\" и \"дата окончания\" совпадают")
        else:
            self.clear_highlight(self.dateTimeEditStartExperiment)
            self.clear_highlight(self.dateTimeEditFinishExperiment)


        if errors:
            self.show_error_message("\n".join(errors))
            return False

        return True

    def highlight_field(self, field: QWidget):
        """ Подсветка поля с ошибкой """
        field.setStyleSheet("border: 1px solid red; background-color: #FFE6E6;")

    def clear_highlight(self, field: QWidget):
        """ Убрать подсветку """
        field.setStyleSheet("")

    def show_error_message(self, message):
        """ Вывод окна с предупреждением о том что невозможно создать расписание """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Заполните обязательные поля")
        msg.setText("Пожалуйста, заполните следующие поля:")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _upload(self, schedule: ScheduleData):
        """ Загрузка данных расписания """
        # experiment
        self.set_combobox_value(self.comboBoxExperiment, schedule.experiment.name)

        # object
        self.LineEditObject.setText(schedule.object.name)

        # model
        models = {"EMG-SENS-": "EMGsens"}
        self.set_combobox_value(self.comboBoxModelDevice, models[schedule.device.model])

        # serial number
        self.LineEditSnDevice.setText(str(schedule.device.serial_number))

        # schedule
        # start time
        st = schedule.datetime_start
        q_st = QDateTime(QDate(st.year, st.month, st.day), QTime(st.hour, st.minute, st.second))
        self.dateTimeEditStartExperiment.setDateTime(q_st)
        self.dateTimeEditStartExperiment.setMinimumDateTime(q_st)

        # finish time
        ft = schedule.datetime_finish
        q_ft = QDateTime(QDate(ft.year, ft.month, ft.day), QTime(ft.hour, ft.minute, ft.second))
        self.dateTimeEditFinishExperiment.setDateTime(q_ft)

        # interval
        interval = self.convert_seconds_with_identifier(seconds=schedule.sec_interval)
        self.set_combobox_value(self.comboBoxInterval, interval)

        # param records
        # record duration
        duration = self.convert_seconds_with_identifier(seconds=schedule.sec_duration)
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

    def setDefaults(self):
        """ Установка значений по умолчанию """
        if self.default_schedule is not None:
            logger.debug(f"Установка настроек по умолчанию из структуры расписания: {self.default_schedule}")
            self.has_unsaved_changes = False
            self._upload(self.default_schedule)
            return

        logger.info("Установка настроек по умолчанию")

        # set text
        self.comboBoxExperiment.setPlaceholderText("Не выбрано")

        # set index
        self.comboBoxFormat.setCurrentIndex(1)
        self.comboBoxModelDevice.setCurrentIndex(0) # set EMGsens
        self.comboBoxSamplingRate.setCurrentIndex(0)
        self.comboBoxDuration.setCurrentIndex(0)
        self.comboBoxInterval.setCurrentIndex(0)

        crt_dt = QDateTime.currentDateTime()
        # установка минимального времени для начала записи
        self.dateTimeEditStartExperiment.setMinimumDateTime(crt_dt.addSecs(60))
        # установка минимального времени для конца записи
        self.dateTimeEditFinishExperiment.setMinimumDateTime(crt_dt.addSecs(60))
        self.dateTimeEditFinishExperiment.setDateTime(crt_dt.addDays(1))

        if (self.LineEditSnDevice.text().strip() == ""
                or self.LineEditObject.text().strip() == ""
                or self.comboBoxExperiment.currentIndex() == -1):
            self.has_unsaved_changes = False

    def getSchedule(self) -> Optional[ScheduleData]:
        """ Формирование структуры данных с описанием Расписания """
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

        start_datetime = self.dateTimeEditStartExperiment.dateTime().toPython().replace(microsecond=0, second=0)
        finish_datetime = self.dateTimeEditFinishExperiment.dateTime().toPython().replace(microsecond=0, second=0)
        sec_interval = self.convert_to_seconds_by_last_word(self.comboBoxInterval.currentText())
        sec_duration = self.convert_to_seconds_by_last_word(self.comboBoxDuration.currentText())

        file_format = list(self.comboBoxFormat.currentData().value.values())[0]
        sampling_rate = int(self.comboBoxSamplingRate.currentText().split()[0])

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

    def convert_to_seconds_by_format(self, duration: str, time_format: str) -> int:
        sec_duration = 0

        if time_format == "[mm:ss]":    # duration
            duration = "0:" + duration
        if time_format == "[hh:mm]":    # interval
            duration = duration + ":0"

        time = duration.replace(":", " ").split()[::-1]
        for i, t in enumerate(time):
            sec_duration += int(t) * (60 ** i)
        return sec_duration

    def convert_to_seconds_by_last_word(self, value: str):
        """ Конвертация в секунды по последнему слову """
        seconds = None

        value, last_word = tuple(value.split(" "))
        if value.isdigit():
            if "минут" in last_word:
                seconds = int(value) * 60
            elif "час" in last_word:
                seconds = int(value) * 3600

        if seconds is None:
            raise ValueError("Невозможно выполнить конвертацию в секунды")

        return seconds

    def convert_seconds_to_str_by_format(self, seconds: int, time_format: str) -> str | None:
        if time_format == "[mm:ss]":    # duration
            s = seconds % 60
            m = seconds // 60
            return f"{m:02d}:{s:02d}"
        if time_format == "[hh:mm]":    # interval
            m = seconds // 60 % 60
            h = seconds // 3600
            return f"{h:02d}:{m:02d}"
        return None

    def convert_seconds_with_identifier(self, seconds: int) -> str | None:
        minutes = seconds // 60
        if minutes < 60:
            # Для минут кратных 10
            if minutes % 10 == 0:
                return f"{minutes} минут"
            # Для 30 минут
            elif minutes == 30:
                return "30 минут"
            elif 2 <= minutes <= 4:
                return f"{minutes} минуты"
            elif minutes == 1:
                return f"1 минута"
            else:
                # Округляем до ближайшего кратного 10
                rounded_minutes = round(minutes / 10) * 10
                return f"{rounded_minutes} минут"
        else:
            # Преобразуем в часы
            hours = minutes // 60
            if hours == 1:
                return "1 час"
            elif 2 <= hours <= 4:
                return f"{hours} часа"
            else:
                return f"{hours} часов"

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



class DlgCreateExperiment(Ui_DlgInputExperiment, QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))


    def getExperiment(self) -> ExperimentData:
        exp_d = ExperimentData(name=self.lineEditExperiment.text())
        return exp_d
