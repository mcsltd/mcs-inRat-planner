import datetime
import logging
import os
import uuid
from configparser import ConfigParser
from copy import copy

from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox, QFileDialog, QAbstractItemView, \
    QTableView
from PySide6.QtGui import QIcon

# scheduler
from apscheduler.schedulers.qt import QtScheduler
from sqlalchemy.orm import Session

from device.ble_manager import BleManager, RecordingTaskData

# table
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE, ScheduleState, RecordStatus
from db.database import connection
from db.models import Schedule, Object, Device, Record
from structure import ScheduleData, RecordData

# ui
from resources.v1.main_window import Ui_MainWindow
from ui.about_dialog import AboutDialog
from ui.helper_dialog import DialogHelper
from ui.schedule_dialog import DlgCreateSchedule
from tools.modview import GenericTableWidget
from util import delete_file, copy_file

PATH_TO_ICON = "resources/v1/icon_app.svg"

# database
from db.queries import get_count_records, get_count_error_records, \
    get_object_by_schedule_id, get_experiment_by_schedule_id, \
    get_path_by_record_id, soft_delete_records, get_all_record_time, all_restore
from ui.settings_dialog import DlgMainConfig
from ui.monitor_dialog import SignalMonitor
from ui.stream_dialog import BLESignalViewer

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    preferences_file: str = "config.ini"

    maxConnectDevicesChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")
        self.setWindowIcon(QIcon(PATH_TO_ICON))

        # init ble manager
        self.ble_manager = BleManager()
        self.ble_manager.start()

        # init scheduler
        self.scheduler = QtScheduler()
        self.scheduler.start()
        self.init_jobs()

        # create view for table Schedule and History
        self.tableModelSchedule = GenericTableWidget()
        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=[])
        self.tableModelSchedule.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.labelSchedule.setText(f"Расписание (всего: 0)")

        self.tableModelHistory = GenericTableWidget()
        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=[])
        self.labelHistory.setText(f"Записей (всего: 0)")

        # добавление таблиц в layout
        self.verticalLayoutHistory.addWidget(self.tableModelHistory)
        self.verticalLayoutSchedule.addWidget(self.tableModelSchedule)

        # соединение сигналов с функциями
        self.ble_manager.signal_schedule_state.connect(self.handle_schedule_state)
        self.ble_manager.signal_record_result.connect(self.handle_record_result)
        self.ble_manager.signal_device_error.connect(self.on_ble_manager_error)
        self.maxConnectDevicesChanged.connect(self.ble_manager.set_max_connected_devices)

        # tables
        self.tableModelSchedule.clicked.connect(self.sort_records_by_schedule_id)
        self.tableModelSchedule.clicked.connect(self.on_selection_changed)
        self.tableModelSchedule.doubleClicked.connect(self.clicked_schedule)
        self.tableModelHistory.doubleClicked.connect(self.show_record_ecg)

        # buttons
        self.pushButtonAddSchedule.clicked.connect(self.add_schedule)
        self.pushButtonUpdateSchedule.clicked.connect(self.update_schedule)
        self.pushButtonDeleteSchedule.clicked.connect(self.delete_schedule)
        self.pushButtonDownloadRecords.clicked.connect(self.copy_records)
        self.actionSettings.triggered.connect(self.configuration_clicked)
        self.actionAbout.triggered.connect(self.about_clicked)
        self.actionExit.triggered.connect(self.close)

        self.installEventFilter(self)

        # загрузить в таблицы данные
        self.update_content_table_schedule()
        self.update_content_table_history()

        # деактивация кнопок
        self.pushButtonUpdateSchedule.setEnabled(False)
        self.pushButtonDeleteSchedule.setEnabled(False)

        # загрузка настроек
        self.get_preferences()

    def on_selection_changed(self):
        """ Обработка нажатия на строки в таблице Schedule """
        current_index = self.tableModelSchedule.currentIndex()
        if current_index.isValid():
            self.pushButtonUpdateSchedule.setEnabled(True)
            self.pushButtonDeleteSchedule.setEnabled(True)

    def eventFilter(self, watched, event, /):
        """ Фильтр событий для обработки кликов вне таблицы """
        if event.type() == event.Type.MouseButtonPress:

            if not self.tableModelSchedule.geometry().contains(event.scenePosition().toPoint()):
                self.tableModelSchedule.clearSelection()
                self.pushButtonUpdateSchedule.setEnabled(False)
                self.pushButtonDeleteSchedule.setEnabled(False)

                self.update_content_table_history()

        return super().eventFilter(watched, event)

    def copy_records(self):
        """ Скопировать выбранные пользователем файлы в выбранную директорию """
        records = self.tableModelHistory.get_selected_records()

        if not records:
            DialogHelper.show_confirmation_dialog(
                self,
                title="Не выбраны записи для копирования",
                message="Пожалуйста, выберите записи, которые Вы хотите скопировать.",
                btn_no=False,
                icon=QMessageBox.Icon.Information
            )
            return

        path_to_copy = QFileDialog.getExistingDirectory(
            self, "Выберите папку для копирования записей", "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks, )

        for rec in records:
            err = copy_file(path_to_copy, rec)
            if err:
                DialogHelper.show_confirmation_dialog(
                    self,
                    title="Ошибка копирования",
                    message=err,
                    btn_no=False,
                    yes_text="Ok",
                    icon=QMessageBox.Icon.Warning
                )
                continue
            logger.info(f"Файл {rec.path} был скопирован в папку: {path_to_copy}")

    def get_preferences(self):
        """ Установка начальных настроек """
        config = ConfigParser()

        # проверка есть ли файл настроек
        if not os.path.exists(self.preferences_file):
            self.maxConnectDevicesChanged.emit(2) # по умолчанию
            return None

        config.read(self.preferences_file)
        # config.read_file(self.preferences)
        if not (config.has_option("Settings", "max_connected_device")):
            return

        cnt_devices = config.getint("Settings", "max_connected_device")
        self.maxConnectDevicesChanged.emit(cnt_devices)
        return

    def save_preferences(self, cnt_device: int):
        """ Сохранение начальных настроек """
        config = ConfigParser()

        # проверка есть ли файл настроек и секция
        if (os.path.exists(self.preferences_file) and config.has_option("Settings", "max_connected_device")):
            config.set("Settings", "max_connected_device", str(cnt_device))
        else:
            config.add_section("Settings")
            config.set("Settings", "max_connected_device", str(cnt_device))

        with open(self.preferences_file, "w") as config_file:
            config.write(config_file)

    def about_clicked(self):
        dlg = AboutDialog(self)
        dlg.exec()

    @connection
    def init_jobs(self, session):
        """ Создать задачи записи ЭКГ при старте приложения """
        logger.info("Инициализация задач записи ЭКГ...")

        cnt_job = 0
        schedules: list[Schedule] = Schedule.get_all_schedules(session)
        for s in schedules:
            now = datetime.datetime.now()

            schedule = s.to_dataclass(session)
            schedule_id = schedule.id
            dt = datetime.timedelta(seconds=(schedule.sec_duration + schedule.sec_interval))

            # проверка на случай уже созданного расписания
            job = self.scheduler.get_job(job_id=str(schedule_id))
            if job is not None:
                logger.info(f"Задача для расписания с {schedule_id} уже создана")

            if now >= schedule.datetime_finish:
                logger.debug(f"Время действия расписания истекло: {schedule.datetime_finish} для {schedule.id}")
                continue

            last_record = Record.get_last_record(schedule_id, session) # последняя запись в таблице Records
            if last_record is None:
                logger.debug(f"Для объекта {schedule.object.name} не было найдено записей!")
                start_time = schedule.datetime_start
            else:
                last_record = last_record.to_dataclass()
                start_time = last_record.datetime_start + dt  # время следующей запланированной записи

            if now > start_time: # проверка если запланированная запись отстаёт от текущего времени
                logger.info(f"Запланированное время записи {str(start_time)} меньше чем текущее время {str(now)}")
                template_missed_record = RecordData(
                    schedule_id=schedule_id,
                    datetime_start=start_time, sec_duration=0,
                    file_format=schedule.file_format, sampling_rate=schedule.sampling_rate,
                    status=RecordStatus.ERROR.value)

                start_time = self.fill_missed_records(
                    template_missed_record=template_missed_record, time_now=now, delta_time=dt, session=session)

            self.create_job(schedule, start_time=start_time)
            cnt_job += 1

        logger.info(f"Инициализация задач закончена. Всего проинициализировано задач: {cnt_job}")

    def fill_missed_records(self, template_missed_record: RecordData, time_now: datetime.datetime, delta_time: datetime.timedelta, session: Session) -> datetime.datetime:
        """ Заполнение пропущенных записей в таблице Record и возврат следующего времени записи """
        next_record_time = template_missed_record.datetime_start
        while time_now > next_record_time:
            # обновление шаблона
            new_record = copy(template_missed_record)
            new_record.id = uuid.uuid4()
            new_record.datetime_start = next_record_time

            logger.info(f"Была пропущена запись ЭКГ в момент времени {str(new_record.datetime_start)}")
            Record.from_dataclass(new_record).create(session) # создать запись в базе данных
            next_record_time += delta_time
            logger.info(f"Запланирована запись в {str(next_record_time)}")

        return next_record_time

    def create_job(self, schedule: ScheduleData, start_time: datetime.datetime):
        """ Установка задачи в планировщик """

        # ToDo: проблема с обработкой

        self.scheduler.add_job(
            self._create_record,
            args=(schedule, start_time),
            trigger="interval",
            seconds=schedule.sec_interval,
            id=str(schedule.id),
            next_run_time=start_time,
        )
        logger.info(
            f"Создано расписание: {str(schedule.id)};"
            f" запланированное время старта: {start_time.replace(microsecond=0)};"
            f" длительность записи: {schedule.sec_duration}"
        )

    def _create_record(self, schedule: ScheduleData, start_time: datetime.datetime) -> None:
        """ Добавление задачи по съёму ЭКГ в BleManager """
        logger.info(f"Начало записи ЭКГ: {start_time} по расписанию {schedule.id}")

        self.ble_manager.add_task(
            task=RecordingTaskData(
                schedule_id=schedule.id,
                device=schedule.device,
                start_time=start_time,
                finish_time=start_time + datetime.timedelta(seconds=schedule.sec_duration),
                file_format=schedule.file_format,
                sampling_rate=schedule.sampling_rate
            )
        )

    @connection
    def handle_schedule_state(self, schedule_id: UUID, status: ScheduleState, session):
        """ Обработчик сигнала (signal_schedule_state) состояния расписания определяемый BleManager """
        schedule = Schedule.find([Schedule.id == schedule_id], session)
        if schedule is None:
            return

        if not self.tableModelSchedule.modify_value_by_id(row_id=schedule_id, column_name="Статус", value=status.value):
            raise ValueError(f"Не удалось обновить статус для расписания с индексом: {schedule_id}")

    @connection
    def handle_record_result(self, record_data: RecordData, session):
        """ Обработка  сигнала (signal_record_result) из BleManager c результатом записи сигнала """

        schedule_id = record_data.schedule_id
        schedule = Schedule.find([Schedule.id == schedule_id], session)

        if schedule is None:
            record_id = Record.from_dataclass(record_data).create(session)
            soft_delete_records(schedule_id, session)

        record_id = Record.from_dataclass(record_data).create(session)
        logger.debug(f"Добавлена запись в базу данных: {record_id}")

        # Todo: обновить информацию в таблице "Расписания" по schedule_id
        self.update_content_table_schedule()

        # обновить отображение данных в таблице Records
        self.update_content_table_history()

    @connection
    def add_schedule(self, session) -> None:
        """ Добавление нового расписания и создание задачи для записи ЭКГ """
        dlg = DlgCreateSchedule()
        code = dlg.exec()

        if code == QDialog.DialogCode.Accepted:
            schedule: ScheduleData = dlg.getSchedule()

            if schedule is None:
                logger.error("An error occurred while creating the schedule")
                return

            # add object in db
            obj_id = Object.from_dataclass(schedule.object).create(session)
            logger.info(f"Добавлен объект: id={obj_id}")

            device_id = Device.from_dataclass(schedule.device).create(session)
            logger.info(f"Добавлено устройство: id={device_id}")

            # add schedule in db
            schedule_id = Schedule.from_dataclass(schedule).create(session)
            logger.info(f"Добавлено расписание: id={schedule_id}")

            time = schedule.datetime_start
            self.create_job(schedule, start_time=time)

            # fill table Schedule
            self.update_content_table_schedule()
            logger.info("Расписание было добавлено в базу данных и таблицу")

    @connection
    def update_content_table_schedule(self, session):
        logger.info("Обновление всех данных в таблице \"Расписание\"")
        table_data = []

        schedules: list[Schedule] = Schedule.get_all_schedules(session)
        for schedule in schedules:

            schedule: ScheduleData = schedule.to_dataclass(session)

            schedule_id = schedule.id
            experiment_name = schedule.experiment.name
            start_datetime = schedule.datetime_start
            finish_datetime = schedule.datetime_finish
            obj = schedule.object.name
            device = schedule.device.ble_name

            status = self.ble_manager.get_device_status(device_id=schedule.device.id)

            interval = self.convert_seconds_to_str(schedule.sec_interval, mode="short")
            duration = self.convert_seconds_to_str(schedule.sec_duration, mode="short")
            all_records_time = self.convert_seconds_to_str(get_all_record_time(schedule.id), mode="full")
            all_records = get_count_records(schedule.id)
            error_record = get_count_error_records(schedule.id)
            params = f"{schedule.file_format}; {schedule.sampling_rate} Гц"

            table_data.append([schedule_id,experiment_name,obj,start_datetime,finish_datetime,device,status,interval,duration,all_records_time,all_records,error_record,params,])

        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=table_data)
        # update label Schedule
        self.labelSchedule.setText(f"Расписание (всего: {len(table_data)})")

    def sort_records_by_schedule_id(self):
        """ Сортировка строк в таблице История по идентификатору расписания """
        schedule_id = None
        schedule_row = self.tableModelSchedule.get_selected_data()

        if isinstance(schedule_row, list):
            schedule_id = schedule_row[0]

        if isinstance(schedule_id, str):
            try:
                schedule_id = uuid.UUID(schedule_id)
            except Exception as exc:
                logger.error(f"Не удалось преобразовать {schedule_id=} в тип UUID")

        if schedule_id is not None:
            logger.debug(f"Данные в таблице \"История\" отсортированы по идентификатору {schedule_id}")

        self.update_content_table_history(schedule_id)

    @connection
    def update_content_table_history(self, schedule_id: uuid.UUID | None = None, session: Session | None=None) -> None:
        """ Обновить данные в таблице Записей """
        logger.info("Обновление всех данных в таблице \"Записи\"")

        table_data = []
        records: list[Record] = Record.fetch_all(session)
        idx = 1
        for rec in records:

            rec = rec.to_dataclass()
            start_time = rec.datetime_start
            duration = self.convert_seconds_to_str(rec.sec_duration, mode="full")
            experiment = get_experiment_by_schedule_id(rec.schedule_id)
            obj = get_object_by_schedule_id(rec.schedule_id)
            file_format = rec.file_format

            if (schedule_id is None or schedule_id == rec.schedule_id) and rec.status == RecordStatus.OK.value:
                table_data.append([rec.id, idx, start_time, duration, experiment, obj, file_format,])
                idx += 1

        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=table_data)

        # обновление
        if schedule_id is not None:
            schedule = Schedule.find([schedule_id == Schedule.id], session).to_dataclass(session)
            self.labelHistory.setText(f"Записи объекта \"{schedule.object.name}\" (всего: {len(table_data)})")
            return

        self.labelHistory.setText(f"Записей (всего: {len(table_data)})")

    @connection
    def update_schedule(self, session) -> None:
        """ Обработчик кнопки изменения расписаний """
        row_data = self.tableModelSchedule.get_selected_data()
        if row_data is None:
            return None

        schedule_id = row_data[0]
        schedule: Schedule = Schedule.find([Schedule.id == schedule_id], session)
        if not schedule:
            return None
        schedule_data: ScheduleData = schedule.to_dataclass(session)

        device_id = schedule_data.device.id
        if self.ble_manager.has_recording_task(device_id=device_id):
            DialogHelper.show_confirmation_dialog( parent=self, title="Изменение расписания",
                    message=f"На текущий момент для объекта \"{schedule.object.name}\" ведётся регистрация ЭКГ.\n"
                            f"Нельзя изменить расписание. Дождитесь конца регистрации ЭКГ.", btn_no=False, yes_text="Ок")
            return

        #  во время изменения расписания может начаться запись, надо остановить job
        job = self.scheduler.get_job(job_id=str(schedule_id))
        if job is not None:
            logger.debug(f"Расписание поставлено на паузу: {schedule_id}")
            self.scheduler.pause_job(job_id=str(schedule_id))

        dlg = DlgCreateSchedule(schedule_data)
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule_data: ScheduleData = dlg.getSchedule()

            if schedule_data is None:
                logger.error("Возникла ошибка при обновлении расписания")
                return

            # проверка есть ли расписание в бд
            has_schedule = Schedule.find([Schedule.id == schedule.id], session)
            if has_schedule is None:
                raise ValueError(f"В базе данных не найдено расписание с индексом: {schedule.id}")
            has_schedule.update(session, **schedule_data.to_dict_with_ids())
            logger.info("Расписание было добавлено в базу данных и таблицу")

            start_time = schedule_data.datetime_start
            job =  self.scheduler.get_job(str(schedule_id))
            if job is not None:
                self.scheduler.remove_job(job_id=str(schedule_id))
            self.create_job(schedule_data, start_time=start_time)

            # fill table Schedule
            self.update_content_table_schedule()
            return

        if job is not None:
            self.scheduler.resume_job(job_id=str(schedule_id))
        return None

    @connection
    def delete_schedule(self, session) -> None:
        """ Обработчик кнопки удаления расписаний """
        # получить удаляемую строку из таблицы
        schedule_data = self.tableModelSchedule.get_selected_data()
        if schedule_data is None:
            return None
        schedule_id = schedule_data[0]
        schedule = Schedule.find([Schedule.id==schedule_id], session)

        if not schedule:
            return None

        schedule_data = schedule.to_dataclass(session)
        # проверка есть ли для устройства активные задачи
        device_id = schedule_data.device.id
        if self.ble_manager.has_recording_task(device_id=device_id):
            DialogHelper.show_confirmation_dialog(
                    parent=self, title="Удаление расписания",
                    message=f"На текущий момент для объекта \"{schedule_data.object.name}\" ведётся регистрация ЭКГ.\n"
                            f"Нельзя удалить расписание. Дождитесь конца регистрации ЭКГ.", btn_no=False, yes_text="Ok")
            return None
        else:
            if not DialogHelper.show_confirmation_dialog(
                parent=self, title="Удаление расписания",
                message=f"Вы уверены что хотите удалить расписание для объекта \"{schedule_data.object.name}\"?"):
                return None

        # остановить и удалить задачи из расписания
        job = self.scheduler.get_job(job_id=str(schedule_id))
        if job is not None:
            logger.debug(f"Удалено расписание из планировщика с индексом: {str(schedule_id)}")
            self.scheduler.remove_job(job_id=str(schedule_id))

        # удалить (пометить) расписание из БД
        schedule.soft_delete(session)

        self.update_content_table_schedule()
        logger.debug(f"Удалено расписание из базы данных с индексом: {str(schedule_id)}")
        logger.debug(f"Удалено расписание из таблицы с индексом: {str(schedule_id)}")

        # удалить записи для расписания в history
        soft_delete_records(schedule_id, session)

        self.update_content_table_history()
        logger.debug(f"Удалены записи для расписания с индексом: {str(schedule_id)}")

        Device.find([Device.id==schedule_data.device.id], session).soft_delete(session)
        Object.find([Object.id==schedule_data.object.id], session).soft_delete(session)
        return None

    @connection
    def show_record_ecg(self, idx, session):
        """ Запустить монитор сигналов """
        data = self.tableModelHistory.get_selected_data()
        record_id = data[0]
        record = Record.find([Record.id==record_id], session)

        if record is None:
            DialogHelper.show_confirmation_dialog(
                self,
                title="Ошибка", message="Не найдена запись ЭКГ", yes_text="Ok",
                icon=QMessageBox.Icon.Critical, btn_no=False
            )
            return
        record_data: RecordData = record.to_dataclass()

        schedule = Schedule.find([Schedule.id == record_data.schedule_id], session)
        if schedule is None:
            DialogHelper.show_confirmation_dialog(
                self,
                title="Ошибка", message="Не найдено расписание записи ЭКГ", yes_text="Ok",
                icon=QMessageBox.Icon.Critical, btn_no=False
            )
            return
        schedule_data: ScheduleData = schedule.to_dataclass(session)

        monitor = SignalMonitor(schedule_data=schedule_data)
        monitor.load_record(record_data=record_data)
        monitor.exec()

    @connection
    def clicked_schedule(self, index, session):
        """ Обработчик двойного нажатия на строку в таблице Schedule """
        # ToDo: обработка случаев: 1) произошел конец записи; 2) устройство ещё не записывает; 3) устройство записало сигнал; 4) возможность получения сигналов с неск. устр.
        raw_data = self.tableModelSchedule.get_selected_data()
        schedule_id = raw_data[0]

        # получение параметров запущенного устройства
        schedule = Schedule.find([Schedule.id == schedule_id], session)
        if schedule is None:
            DialogHelper.show_confirmation_dialog(
                self,
                title="Ошибка", message="Не найдено расписание записи ЭКГ", yes_text="Ok",
                icon=QMessageBox.Icon.Critical, btn_no=False
            )
            return

        schedule_data: ScheduleData = schedule.to_dataclass(session)

        device_id = schedule_data.device.id
        if self.ble_manager.get_device_status(device_id) == ScheduleState.ACQUISITION.value:
            dlg = BLESignalViewer(schedule_data=schedule_data)
            self.ble_manager.signal_data_received.connect(dlg.accept_signal)
            dlg.exec()
            return

        job = self.scheduler.get_job(job_id=str(schedule_id))
        if job is not None:
            str_time = str(job.next_run_time).split("+")[0]
            DialogHelper.show_confirmation_dialog(
                parent=self, title=f"Информация о расписании",
                btn_no=False, yes_text="Ок", message=f"Регистрация ЭКГ для объекта \"{schedule_data.object.name}\""
                                                     f" запланирована на {str_time}.")

    def configuration_clicked(self):
        """ Активация окна настроек """
        dlg = DlgMainConfig(cnt_device=self.ble_manager.max_connected_devices)

        dlg.signals.max_devices_changed.connect(self.on_max_devices_changed)
        dlg.signals.archive_restored.connect(self.on_archive_restored)
        dlg.signals.archive_deleted.connect(self.on_archive_deleted)
        dlg.signals.data_changed.connect(self.update_data)

        ok = dlg.exec()

    def on_max_devices_changed(self, cnt_device):
        """ Обработчик изменения количества одновременно подключенных устройств """
        logger.info(f"Максимальное количество одновременно подключенных устройств: {cnt_device=}")
        self.save_preferences(cnt_device)
        self.maxConnectDevicesChanged.emit(cnt_device)

    def update_data(self):
        """ Обновление данных в таблице """
        self.update_content_table_history()
        self.update_content_table_schedule()

    def on_archive_restored(self):
        """ Обработчик сигнала восстановления архивных расписаний, объектов, устройств """
        logger.info(f"Восстановление архивных расписаний, объектов, устройств")

        all_restore()               # восстановить записи в БД
        self.init_jobs()            # создать задачи для восстановленных расписаний

        self.update_content_table_schedule()
        self.update_content_table_history()

    @connection
    def on_archive_deleted(self, session):
        """ Обработчик сигнала удаления архивных расписаний, объектов, устройств """
        logger.info(f"Удаление архивных расписаний, объектов, устройств")

        archived_schedules = Schedule.fetch_all_archived([], session)
        for schedule in archived_schedules:
            if schedule is None:
                continue
            schedule_data = schedule.to_dataclass(session, is_deleted=True)
            schedule_id = schedule_data.id
            device_data = schedule_data.device
            object_data = schedule_data.object

            # удалить расписания
            schedule.delete(session)

            # удаление записей
            archived_records = Record.fetch_all_archived([Record.schedule_id == schedule_id], session)
            for rec in archived_records:
                if rec is not None:
                    rec_data = rec.to_dataclass()
                    if delete_file(file_path=rec_data.path):
                        logger.debug(f"Файл записи ЭКГ для расписания {schedule_data.id} был удален")
                    rec.delete(session)

            # удалить объекты
            if object_data is None:
                logger.error(f"Объект для расписания {schedule_id} не был найден")
            else:
                archived_obj = Object.find_archived([Object.id == object_data.id], session)
                if archived_obj is not None:
                    logger.debug(f"Объект {object_data.name} был удален")
                    archived_obj.delete(session)

            # удалить устройства
            if device_data is None:
                logger.error(f"Устройство для расписания {schedule_id} не было найдено")
            else:
                archived_device = Device.find_archived([Device.id == device_data.id], session)
                if archived_device is not None:
                    logger.debug(f"Устройство {device_data.ble_name} было удалено")
                    archived_device.delete(session)

    def on_ble_manager_error(self, device_id, description):
        """ Обработчик выводящий сообщения о проблемах с устройством """
        DialogHelper.show_confirmation_dialog(
            self, title="Предупреждение", yes_text="Ок", icon=QMessageBox.Icon.Warning,
            message=description, btn_no=False)

    def closeEvent(self, event, /):
        """ Обработка закрытия приложения """
        # ToDo: проверять ble manager на выполнение задач
        self.ble_manager.stop()

    @staticmethod
    def convert_seconds_to_str(seconds: int, mode: str = "smart") -> str:
        """
        Конвертирует секунды в строковое представление времени
        """
        if not isinstance(seconds, int):
            raise ValueError("Seconds is not int")

        if seconds < 0:
            return "00:00"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if mode == "full":
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

        elif mode == "short":
            if hours > 0:
                if minutes == 0:
                    return f"{hours} ч."
                else:
                    return f"{hours} ч. {minutes} мин."
            elif minutes > 0:
                if secs == 0:
                    return f"{minutes} мин."
                else:
                    return f"{minutes} мин. {secs} с."
            else:
                return f"{secs} с."

        elif mode == "compact":
            if hours > 0:
                return f"{hours}:{minutes:02d}" if secs == 0 else f"{hours}:{minutes:02d}:{secs:02d}"
            elif minutes > 0:
                return f"{minutes}:{secs:02d}"
            else:
                return f"0:{secs:02d}"

        else:  # smart mode (по умолчанию)
            if hours > 99:
                return "99:59:59+"
            elif hours > 0:
                return f"{hours:02d}:{minutes:02d}" if secs == 0 else f"{hours:02d}:{minutes:02d}:{secs:02d}"
            elif minutes > 0:
                return f"{minutes:02d}" if secs == 0 else f"{minutes:02d}:{secs:02d}"
            else:
                return f"00:{secs:02d}"

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    try:
        window = MainWindow()
        window.showMaximized()
        # window.show()
    except Exception as exc:
        print(f"Возникла ошибка в работе программы: {exc}")
    finally:
        app.exec()



# # проверка есть ли объект в бд
# has_obj = Object.find([Object.id == schedule.object.id], session)
# if has_obj is None:
#     obj_id = Object.from_dataclass(schedule.object).create(session)
#     logger.info(f"Добавлен новый объект: id={obj_id}")

# # проверка есть ли устройство в бд
# has_device = Device.find([Device.id == schedule.device.id], session)
# if has_device is None:
#     device_id = Device.from_dataclass(schedule.device).create(session)
#     logger.info(f"Добавлено устройство: id={device_id}")