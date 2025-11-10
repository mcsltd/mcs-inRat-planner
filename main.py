import datetime
import logging
import uuid
from copy import copy

from uuid import UUID
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox
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
from ui.helper_dialog import DialogHelper
from ui.schedule_dialog import DlgCreateSchedule
from tools.modview import GenericTableWidget
PATH_TO_ICON = "resources/v1/icon_app.svg"

# database
from db.queries import get_count_records, get_count_error_records, \
    get_object_by_schedule_id, get_experiment_by_schedule_id, \
    get_path_by_record_id, soft_delete_records, get_all_record_time
from ui.settings_dialog import DlgMainConfig
from ui.monitor_dialog import SignalMonitor
from ui.stream_dialog import BLESignalViewer

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

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

        # tables
        self.tableModelSchedule.clicked.connect(self.sort_records_by_schedule_id)
        self.tableModelSchedule.doubleClicked.connect(self.clicked_schedule)

        self.tableModelHistory.doubleClicked.connect(self.run_monitor)

        # buttons
        self.pushButtonAddSchedule.clicked.connect(self.add_schedule)
        self.pushButtonUpdateSchedule.clicked.connect(self.update_schedule)
        self.pushButtonDeleteSchedule.clicked.connect(self.delete_schedule)
        self.actionSettings.triggered.connect(self.configuration_clicked)
        self.actionExit.triggered.connect(self.close)

        self.pushButtonDownloadRecords.setDisabled(True)
        self.pushButtonUpdateSchedule.setDisabled(False)

        # загрузить в таблицы данные
        self.update_content_table_schedule()
        self.update_content_table_history()

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

            if now >= schedule.datetime_finish:
                logger.debug(f"Время действия расписания истекло: {schedule.datetime_finish} для {schedule.id}")
                continue

            last_record = Record.get_last_record(schedule_id, session).to_dataclass() # последняя запись в таблице Records
            start_time = last_record.datetime_start + dt        # время следующей запланированной записи
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

    def fill_missed_records(
            self,
            template_missed_record: RecordData,
            time_now: datetime.datetime, delta_time: datetime.timedelta,
            session: Session
    ) -> datetime.datetime:
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

    def handle_schedule_state(self, schedule_id: UUID, status: ScheduleState):
        """ Обработчик сигнала (signal_schedule_state) состояния расписания определяемый BleManager """
        if not self.tableModelSchedule.modify_value_by_id(row_id=schedule_id, column_name="Статус", value=status.value):
            raise ValueError(f"Не удалось обновить статус для расписания с индексом: {schedule_id}")

    @connection
    def handle_record_result(self, record_data: RecordData, session):
        """ Обработка  сигнала (signal_record_result) из BleManager c результатом записи сигнала """

        record_id = Record.from_dataclass(record_data).create(session)
        logger.debug(f"Добавлена запись в базу данных: {record_id}")

        if record_data.status == RecordStatus.ERROR.value:
            schedule_data = Schedule.find([record_data.schedule_id == Schedule.id], session).to_dataclass(session)
            reply = QMessageBox.warning(
                self, f"Ошибка записи ЭКГ",
                f"Возникла ошибка записи с устройства {schedule_data.device.ble_name}.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
            )

        # Todo: обновить информацию в таблице "Расписания" по schedule_id
        self.update_content_table_schedule()

        # обновить отображение данных в таблице Records
        self.update_content_table_history()

    # Schedule
    @connection
    def add_schedule(self, session) -> None:
        """ Добавление нового расписания и создание задачи для записи ЭКГ """
        # experiments = get_experiments()
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

            # ToDo: проверка времени должна быть внутри диалогового окна
            # time = schedule.datetime_start
            # if time <= datetime.datetime.now():
            time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(seconds=10)
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

            interval = self.convert_seconds_to_str(schedule.sec_interval)
            duration = self.convert_seconds_to_str(schedule.sec_duration)
            all_records_time = self.convert_seconds_to_str(get_all_record_time(schedule.id))
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
            duration = self.convert_seconds_to_str(rec.sec_duration)
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
        schedule_data = self.tableModelSchedule.get_selected_data()
        if schedule_data is None:
            return None

        schedule_id = str(schedule_data[0])
        # остановить и удалить задачи из расписания
        job = self.scheduler.get_job(job_id=schedule_id)
        if job is not None:
            logger.debug(f"Удалено расписание из планировщика с индексом: {schedule_id}")
            self.scheduler.remove_job(job_id=schedule_id)

        schedule = Schedule.find([Schedule.id == UUID(schedule_id)], session).to_dataclass(session)
        dlg = DlgCreateSchedule(schedule)
        code = dlg.exec()

        if code == QDialog.DialogCode.Accepted:
            schedule: ScheduleData = dlg.getSchedule()

            if schedule is None:
                logger.error("Возникла ошибка при обновлении расписания")
                return

            # проверка есть ли объект в бд
            has_obj = Object.find([Object.id == schedule.object.id], session)
            if has_obj is None:
                obj_id = Object.from_dataclass(schedule.object).create(session)
                logger.info(f"Добавлен новый объект: id={obj_id}")

            # проверка есть ли устройство в бд
            has_device = Device.find([Device.id == schedule.device.id], session)
            if has_device is None:
                device_id = Device.from_dataclass(schedule.device).create(session)
                logger.info(f"Добавлено устройство: id={device_id}")

            # проверка есть ли расписание в бд
            has_schedule = Schedule.find([Schedule.id == schedule.id], session)
            if has_schedule is None:
                raise ValueError(f"В базе данных не найдено расписание с индексом: {schedule.id}")
            has_schedule.update(session, **schedule.to_dict_with_ids())

            # ToDo: проверка времени должна быть внутри диалогового окна
            # time = schedule.datetime_start
            # if time <= datetime.datetime.now():
            time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(seconds=10)
            self.create_job(schedule, start_time=time)

            # fill table Schedule
            self.update_content_table_schedule()
            logger.info("Расписание было добавлено в базу данных и таблицу")

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

        s = schedule.to_dataclass(session)
        if not DialogHelper.show_confirmation_dialog(
            parent=self, title="Удаление расписания",
            message=f"Вы уверены что хотите удалить расписание для объекта \"{s.object.name}\"?"):
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

        # Device.find([Schedule.id==schedule_data[0]], session).soft_delete(session)
        # Object.find([Object.id==schedule_data[0]], session).soft_delete(session)
        return None

    def run_monitor(self):
        """ Запустить монитор сигналов """
        data = self.tableModelHistory.get_selected_data()
        record_id = data[0]
        path = get_path_by_record_id(record_id=record_id)

        if path is None:
            raise ValueError(f"Path is {path}")

        monitor = SignalMonitor()
        monitor.load_data(path_to_file=path)
        monitor.exec()

    @connection
    def clicked_schedule(self, index, session):
        """ Обработчик двойного нажатия на строку в таблице Schedule """
        # ToDo: обработка случаев: 1) произошел конец записи; 2) устройство ещё не записывает; 3) устройство записало сигнал; 4) возможность получения сигналов с неск. устр.
        data = self.tableModelSchedule.get_selected_data()

        # получение параметров запущенного устройства
        schedule_data = Schedule.find([Schedule.id == data[0]], session).to_dataclass(session)
        device_id = schedule_data.device.id
        device_name = schedule_data.device.ble_name

        if self.ble_manager.get_device_status(device_id) == ScheduleState.ACQUISITION.value:
            dlg = BLESignalViewer(device_id=device_id, device_name=device_name, fs=1000)
            self.ble_manager.signal_data_received.connect(dlg.accept_signal)
            dlg.exec()

    def configuration_clicked(self):
        """ Активация окна настроек """
        dlg = DlgMainConfig()

        # ToDo: устанавливать текущее максимальное кол-во одновременно подключенных устройств
        dlg.signals.max_devices_changed.connect(self.on_max_devices_changed)
        dlg.signals.archive_restored.connect(self.on_archive_restored)
        dlg.signals.archive_deleted.connect(self.on_archive_deleted)

        ok = dlg.exec()

    def on_max_devices_changed(self, max_devices):
        """ Обработчик изменения количества одновременно подключенных устройств """
        logger.info(f"Максимальное количество одновременно подключенных устройств: {max_devices=}")
        # ToDo: ...

    def on_archive_restored(self):
        """ Обработчик сигнала восстановления архивных расписаний, объектов, устройств """
        logger.info(f"Восстановление архивных расписаний, объектов, устройств")
        # ToDo: ...

    def on_archive_deleted(self):
        """ Обработчик сигнала удаления архивных расписаний, объектов, устройств """
        logger.info(f"Удаление архивных расписаний, объектов, устройств")
        # ToDo: ...

    def closeEvent(self, event, /):
        """ Обработка закрытия приложения """
        self.ble_manager.stop()

    @classmethod
    def convert_seconds_to_str(cls, seconds: int) -> str | None:
        if not isinstance(seconds, int):
            raise ValueError("Seconds is not int")

        if seconds / 3600 >= 1:
            return f"{seconds // 3600} ч."
        if seconds / 60 >= 1:
            return f"{seconds // 60} мин."
        return f"{seconds} с."


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
