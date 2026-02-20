import datetime
import logging
import os
import uuid
from configparser import ConfigParser

from uuid import UUID

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox, QFileDialog, QTableView
from PySide6.QtGui import QIcon

# scheduler
from apscheduler.schedulers.qt import QtScheduler
from sqlalchemy.orm import Session

from ble_manager import BleManager

# table
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE, ScheduleState, RecordStatus, Devices
from db.database import connection
from db.models import Schedule, Object, Device, Record
from tools.check_bluetooth import is_bluetooth_enabled
from structure import ScheduleData, RecordData, RecordingTaskData

# ui
from resources.v1.main_window import Ui_MainWindow
from ui.about_dialog import AboutDialog, DialogLicenses
from ui.helper_dialog import DialogHelper
from ui.inrat_controller_dialog import InRatControllerDialog
from ui.schedule_dialog import DlgCreateSchedule
from ui.manage_experiments import ExperimentCRUDWidget
from tools.modview import GenericTableWidget
from util import delete_file, copy_file

from config import PATH_TO_ICON, PATH_TO_LICENSES, app_data

# database
from db.queries import get_count_records, get_count_error_records, \
    get_object_by_schedule_id, get_experiment_by_schedule_id, \
    soft_delete_records, get_all_record_time, all_restore
from ui.settings_dialog import DlgMainConfig
from ui.monitor_dialog import SignalMonitor
from ui.stream_dialog import BLESignalViewer

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    # preferences_file: str = "../config.ini"
    maxConnectDevicesChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")
        self.setWindowIcon(QIcon(PATH_TO_ICON))

        # init ble manager
        self.ble_manager = BleManager()
        if is_bluetooth_enabled():
            self.ble_manager.start()
        else:
            DialogHelper.show_confirmation_dialog(
                parent=self, title="Ошибка работы Bluetooth",
                message="Bluetooth не найден. Убедитесь, что Bluetooth включен.",
                icon=QMessageBox.Icon.Critical, yes_text="Ok", no_text=None
            )

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

        self.actionExperiments.triggered.connect(self.experiments_clicked)
        self.actionSettings.triggered.connect(self.configuration_clicked)
        self.actionLicenses.triggered.connect(self.licenses_clicked)
        self.actionAbout.triggered.connect(self.about_clicked)
        self.actionExit.triggered.connect(self.close)
        self.actionDEBUGActiveSchedule.triggered.connect(self.debug_show_active_schedule_tasks)

        self.installEventFilter(self)

        # загрузить в таблицы данные
        self.update_content_table_schedule()
        self.update_content_table_history()

        # деактивация кнопок
        self.pushButtonUpdateSchedule.setEnabled(False)
        self.pushButtonDeleteSchedule.setEnabled(False)

        # загрузка настроек
        self.get_preferences()

    def debug_show_active_schedule_tasks(self):
        DialogHelper.show_confirmation_dialog(
            parent=self, title="Информация о количестве активных расписаний",
            message=f"Всего активных расписаний: {len(self.scheduler.get_jobs())}",
            yes_text="Да", no_text="Нет",
            icon=QMessageBox.Icon.Information,
        )

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
        if not os.path.exists(app_data.preferences_file):
            self.maxConnectDevicesChanged.emit(2) # по умолчанию
            return None

        config.read(app_data.preferences_file)
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
        if (os.path.exists(app_data.preferences_file) and config.has_option("Settings", "max_connected_device")):
            config.set("Settings", "max_connected_device", str(cnt_device))
        else:
            config.add_section("Settings")
            config.set("Settings", "max_connected_device", str(cnt_device))

        with open(app_data.preferences_file, "w") as config_file:
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
            t_now = datetime.datetime.now()

            schedule = s.to_dataclass(session)
            start_time = schedule.datetime_start
            schedule_id = schedule.id

            if start_time is None: # пропуск незапланированных расписаний
                continue

            # проверка на случай уже созданного расписания
            job = self.scheduler.get_job(job_id=str(schedule_id))
            if job is not None:
                logger.info(f"Задача для расписания с {schedule_id} уже создана")
                continue

            dt = datetime.timedelta(seconds=schedule.sec_interval)
            if t_now > schedule.datetime_finish:
                logger.debug(f"Время действия расписания {schedule.id} истекло {schedule.datetime_finish}")
                continue

            # расчёт времени следующего старта записи по расписанию
            if start_time < t_now:
                n = int((t_now - start_time).total_seconds() // dt.total_seconds()) # кол-во полных запусков за диапазон времени от start_time до now
                start_time = (n + 1) * dt + start_time

                # заполнение в базе данных пропущенных записей
                cnt_skip_rec = self.fill_missed_scheduled_records(schedule, t_now, session)
                logger.debug(f"Для расписания {schedule_id} было пропущено {cnt_skip_rec} записей")

            self.create_job(schedule, start_time=start_time)
            cnt_job += 1
        logger.info(f"Инициализация задач закончена. Всего проинициализировано задач: {cnt_job}")

    def fill_missed_scheduled_records(self, schedule: ScheduleData, t_now: datetime.datetime, session: Session) -> int:
        """ Заполнение пропущенных записей в таблице Record """
        start_time = schedule.datetime_start
        finish_time = schedule.datetime_finish

        # получить последнюю запись сделанную по расписанию
        last_record = Record.get_last_record(schedule.id, session)
        if last_record and last_record.datetime_start > start_time:
            last_time = last_record.datetime_start
            start_idx = int(((last_time - start_time).total_seconds()) // schedule.sec_interval) + 1
        else:
            start_idx = 0   # отсутствуют записи по расписанию

        end_idx = int((t_now - start_time).total_seconds() // schedule.sec_interval)    # количество записей до t_now
        finish_idx = int((finish_time - start_time).total_seconds() // schedule.sec_interval)   # общее кол-во записей
        end_idx = min(end_idx, finish_idx)

        values = []
        for idx in range(start_idx, end_idx + 1):
            record_time = start_time + datetime.timedelta(seconds=idx * schedule.sec_interval)
            values.append({
                'id': uuid.uuid4(), 'schedule_id': schedule.id, 'datetime_start': record_time,
                'sec_duration': 0, 'file_format': schedule.file_format, 'sampling_rate': schedule.sampling_rate,
                'status': RecordStatus.ERROR.value,
            })
        if not values:
            return 0

        session.execute(Record.__table__.insert(), values)
        session.commit()

        return len(values)


    def create_job(self, schedule: ScheduleData, start_time: datetime.datetime):
        """ Установка задачи в планировщик """
        self.scheduler.add_job(
            self._create_record, args=(schedule, start_time),
            trigger="interval", seconds=schedule.sec_interval,
            id=str(schedule.id), next_run_time=start_time,
        )
        logger.info(
            f"Создано расписание: {str(schedule.id)};"
            f" запланированное время старта: {start_time.replace(microsecond=0)};"
            f" длительность записи: {schedule.sec_duration}"
        )

    def _create_record(self, schedule: ScheduleData, start_time: datetime.datetime) -> None:
        """ Добавление задачи по съёму ЭКГ в BleManager """
        logger.info(f"Начало записи ЭКГ: {start_time} по расписанию {schedule.id}")

        # # проверка на истечение времени расписания
        # finish_time = schedule.datetime_finish
        # now_t = start_time + datetime.timedelta(seconds=schedule.sec_duration)
        # if now_t > finish_time:
        #     logger.info(f"Расписания {str(schedule.id)} истекло; текущее время {now_t}; время окончания {finish_time}")
        #     self.scheduler.remove_job(job_id=str(schedule.id))
        #     self.update_content_table_schedule()
        #     return

        self.ble_manager.add_task(
            task=RecordingTaskData(
                schedule_id=schedule.id, experiment=schedule.experiment, device=schedule.device, object=schedule.object,
                start_time=start_time, sec_duration=schedule.sec_duration, file_format=schedule.file_format, sampling_rate=schedule.sampling_rate)
        )

        # проверка на истечение следующего расписания
        finish_time = schedule.datetime_finish
        next_record_time = start_time + datetime.timedelta(seconds=schedule.sec_interval)
        if next_record_time > finish_time:
            logger.info(f"Для расписания {str(schedule.id)} истекло время; следующая запись {next_record_time}; время окончания {finish_time}")

            job = self.scheduler.get_job(str(schedule.id))
            if job is not None:
                self.scheduler.remove_job(job_id=str(schedule.id))
            self.update_content_table_schedule()
            return


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
            if time is not None:
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
            start_datetime = "Не установлено" if schedule.datetime_start is None else schedule.datetime_start
            finish_datetime = "Не установлено" if schedule.datetime_finish is None else schedule.datetime_finish
            obj = schedule.object.name
            device = schedule.device.ble_name

            if schedule.datetime_finish is None or schedule.datetime_start is None:
                status = ScheduleState.UNPLANNED.value
            elif datetime.datetime.now() + datetime.timedelta(seconds=schedule.sec_interval) > schedule.datetime_finish:
                if self.scheduler.get_job(str(schedule_id)):
                    status = ScheduleState.DISCONNECT.value
                else:
                    status = ScheduleState.EXPIRED.value
            else:
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

        # постановка выполнения задачи на паузу во время изменения параметров расписания
        job = self.scheduler.get_job(job_id=str(schedule_id))
        if job is not None:
            logger.debug(f"Расписание поставлено на паузу: {schedule_id}")
            next_run = job.next_run_time
            self.scheduler.pause_job(job_id=str(schedule_id))
        else:
            #  на случай если расписание истекло или незапланированно
            next_run = schedule_data.datetime_finish

        if next_run is not None:
            next_run = next_run.astimezone().replace(tzinfo=None)

        # открытие диалогового окна изменения параметров расписания
        dlg = DlgCreateSchedule(schedule_data)
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule_data_new: ScheduleData = dlg.getSchedule()
            if schedule_data_new is None:
                logger.error("Возникла ошибка при обновлении расписания")
                return

            # проверка есть ли расписание в бд
            has_schedule = Schedule.find([Schedule.id == schedule.id], session)
            if has_schedule is None:
                raise ValueError(f"В базе данных не найдено расписание с индексом: {schedule.id}")
            data = schedule_data_new.to_dict_with_ids()
            has_schedule.update(session, **data)
            logger.info("Расписание было добавлено в базу данных и таблицу")

            start_time = next_run
            # проверка изменения времени старта
            if schedule_data.datetime_start != schedule_data_new.datetime_start:
                start_time = schedule_data_new.datetime_start

            if start_time is not None:
                job = self.scheduler.get_job(str(schedule_id))
                if job is not None:
                    self.scheduler.remove_job(job_id=str(schedule_id))
                self.create_job(schedule_data_new, start_time=start_time)

            # fill table Schedule
            self.update_content_table_schedule()
            return

        # если параметры расписания не были изменены
        if job is not None:
            # активация задачи
            if datetime.datetime.now() > next_run:
                next_run = datetime.datetime.now() + datetime.timedelta(seconds=10)
            job.resume()
            job.modify(next_run_time=next_run)
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
                self, title="Ошибка", message="Не найдена запись ЭКГ", yes_text="Ok", icon=QMessageBox.Icon.Critical,
                btn_no=False
            )
            return
        record_data: RecordData = record.to_dataclass()

        schedule = Schedule.find([Schedule.id == record_data.schedule_id], session)
        if schedule is None:
            DialogHelper.show_confirmation_dialog(
                self,title="Ошибка", message="Не найдено расписание записи ЭКГ", yes_text="Ok",
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
        raw_data = self.tableModelSchedule.get_selected_data()
        schedule_id = raw_data[0]

        # получение параметров запущенного устройства
        schedule = Schedule.find([Schedule.id == schedule_id], session)
        if schedule is None:
            DialogHelper.show_confirmation_dialog(
                self, title="Ошибка", message="Не найдено расписание записи ЭКГ", yes_text="Ok",
                icon=QMessageBox.Icon.Critical, btn_no=False
            )
            return

        schedule_data: ScheduleData = schedule.to_dataclass(session)

        # запуск просмотра стрима сигнала с устройства
        device_id = schedule_data.device.id
        device_status = self.ble_manager.get_device_status(device_id)
        if device_status == ScheduleState.ACQUISITION.value:
            dlg = BLESignalViewer(schedule_data=schedule_data)
            self.ble_manager.signal_data_received.connect(dlg.accept_signal)
            dlg.exec()
            return

        if device_status == ScheduleState.IN_QUEUE.value:
            text_message = f"Устройство {schedule_data.device.ble_name} находится в очереди на подключение."
            DialogHelper.show_confirmation_dialog(parent=self, title=f"Информация о расписании", message=text_message,
                                                  yes_text="Ok", btn_no=False, icon=QMessageBox.Icon.Information)
            return

        if device_status == ScheduleState.CONNECTION.value:
            text_message = f"Выполняется поиск {schedule_data.device.ble_name}."
            DialogHelper.show_confirmation_dialog(parent=self, title=f"Информация о расписании", message=text_message,
                                                  yes_text="Ok", btn_no=False, icon=QMessageBox.Icon.Information)
            return

        job, str_time = None, None
        if schedule_data.datetime_start is not None or schedule_data.datetime_finish is not None:
            # проверка на истечение времени
            if not(schedule_data.datetime_finish < datetime.datetime.now()):
                job = self.scheduler.get_job(job_id=str(schedule_id))
                if job is None:
                    DialogHelper.show_confirmation_dialog(
                        self, title="Ошибка", message="Не найдено расписание записи ЭКГ",
                        yes_text="Ok", icon=QMessageBox.Icon.Critical, btn_no=False)
                    return
                next_run = job.next_run_time.replace(microsecond=0)
                if next_run.tzinfo is not None:
                    next_run = next_run.astimezone().replace(tzinfo=None)
                str_time = next_run.strftime("%Y-%m-%d %H:%M:%S")

        if schedule_data.device.model == Devices.INRAT.value["InRat"]:
            text_message = ""
            if job is not None:
                text_message = f"Регистрация ЭКГ для объекта \"{schedule_data.object.name}\" запланирована на {str_time}."
            elif schedule_data.datetime_start is None or schedule_data.datetime_finish is None:
                text_message = f"Не задано расписание для объекта \"{schedule_data.object.name}\"."
            elif schedule_data.datetime_finish < datetime.datetime.now():
                text_message = f"Расписание регистрации ЭКГ для объекта \"{schedule_data.object.name}\" истекло."

            if DialogHelper.show_action_dialog(parent=self, title=f"Информация о расписании", message=text_message,):
                if job is not None:
                    # постановка расписания на паузу, если пользователь выбрал ручной режим
                    job.pause()

                try:
                    dlg = InRatControllerDialog(parent=self, schedule_data=schedule_data)
                    dlg.signal_record_saved.connect(self.handle_record_result)
                    dlg.exec()
                except Exception as exp:
                    logger.error(f"Ошибка при запуске ручного режима для InRat: {exp}")
                finally:
                    if job is not None:
                        # активация задачи
                        if datetime.datetime.now() > next_run:
                            next_run = datetime.datetime.now() + datetime.timedelta(seconds=10)
                        job.resume()
                        job.modify(next_run_time=next_run)

    def experiments_clicked(self):
        dlg = ExperimentCRUDWidget()
        dlg.signals.data_changed.connect(self.update_content_table_schedule)
        dlg.show()

    def configuration_clicked(self):
        """ Активация окна настроек """
        dlg = DlgMainConfig(cnt_device=self.ble_manager.max_connected_devices)

        dlg.signals.max_devices_changed.connect(self.on_max_devices_changed)
        dlg.signals.archive_restored.connect(self.on_archive_restored)
        dlg.signals.archive_deleted.connect(self.on_archive_deleted)
        dlg.signals.data_changed.connect(self.update_data)

        ok = dlg.exec()

    def licenses_clicked(self):
        dlg = DialogLicenses(parent=self, path_to_licenses=PATH_TO_LICENSES)
        dlg.exec()

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
    except Exception as exc:
        DialogHelper.show_confirmation_dialog(
            parent=None,
            title="Возникла ошибка запуска приложения",
            message=f"Текст ошибки: {exc}",
            icon=QMessageBox.Icon.Critical,
            yes_text="Ok",
            btn_no=False
          )
    finally:
        app.exec()


