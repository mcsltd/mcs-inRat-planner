import datetime
import logging

from uuid import UUID
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox

# scheduler
from apscheduler.schedulers.qt import QtScheduler

from device.ble_manager import BleManager, RecordingTaskData

# table
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE
from db.database import connection
from db.models import Schedule, Object, Device, Record
from monitor import SignalMonitor
from structure import ScheduleData, RecordData
from ui.v1.dlg_main_config import Ui_DlgMainConfig

# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule
from tools.modview import GenericTableWidget

# database
from db.queries import get_count_records, get_count_error_records, \
    get_object_by_schedule_id, get_experiment_by_schedule_id, \
    get_path_by_record_id, restore, soft_delete_records, get_all_record_time

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

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
        self.ble_manager.signal_record_result.connect(self.handle_record_result)

        # tables
        self.tableModelHistory.doubleClicked.connect(self.run_monitor)

        # ToDo: сделать приложение в реальном времени показывающее сигнал с устройства
        self.tableModelSchedule.doubleClicked.connect(self.clicked_schedule)

        # buttons
        self.pushButtonAddSchedule.clicked.connect(self.add_schedule)
        self.pushButtonUpdateSchedule.clicked.connect(self.update_schedule)
        self.pushButtonDeleteSchedule.clicked.connect(self.delete_schedule)
        self.actionSettings.triggered.connect(self.configuration_clicked)
        self.actionExit.triggered.connect(self.close)

        self.pushButtonDownloadRecords.setDisabled(True)
        self.pushButtonUpdateSchedule.setDisabled(False)

        # загрузить в таблицы данные
        self.update_content_table_history()
        self.update_content_table_schedule()

    @connection
    def init_jobs(self, session):
        """ Метод инициализирующий планировщик и загружающий в него расписания записи ЭКГ """
        logger.info("Инициализация задач записи ЭКГ...")

        schedules: list[Schedule] = Schedule.get_all_schedules(session)
        for s in schedules:
            job = s.to_dataclass(session)

            if datetime.datetime.now() >= job.datetime_finish:
                logger.debug(f"Время действия расписания истекло: {job.datetime_finish} для {job.id}")
                return

            self.create_job(job, start_time=job.datetime_start)

    def create_job(self, schedule: ScheduleData, start_time: datetime.datetime):
        """ Планирование задачи записи сигнала ЭКГ по времени """
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
        """
        Создание задачи на подключение и запись BleManager'у
        """
        logger.debug(f"Начало записи ЭКГ: {start_time} по расписанию {schedule.id}")

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
    def handle_record_result(self, record_data: RecordData, session):
        """ Обработка  сигнала (signal_record_result) из BleManager c результатом записи сигнала """
        record_id = Record.from_dataclass(record_data).create(session)
        logger.debug(f"Добавлена запись в базу данных: {record_id}")

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

    @classmethod
    def convert_seconds_to_str(cls, seconds) -> str | None:
        if seconds / 3600 >= 1:
            return f"{seconds // 3600} ч."
        if seconds / 60 >= 1:
            return f"{seconds // 60} мин."
        return f"{seconds} с."

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
            status = "Ожидание"
            interval = self.convert_seconds_to_str(schedule.sec_interval)
            duration = self.convert_seconds_to_str(schedule.sec_duration)
            all_records_time = self.convert_seconds_to_str(get_all_record_time(schedule.id))
            all_records = get_count_records(schedule.id)
            error_record = get_count_error_records(schedule.id)
            params = f"{schedule.file_format}; {schedule.sampling_rate} Гц"

            table_data.append([schedule_id, experiment_name,start_datetime,finish_datetime,obj,device,status,interval,duration,all_records_time,all_records,error_record,params,])

        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=table_data)
        # update label Schedule
        self.labelSchedule.setText(f"Расписание (всего: {len(table_data)})")

    @connection
    def update_content_table_history(self, session) -> None:
        logger.info("Обновление всех данных в таблице \"Записи\"")

        table_data = []
        records: list[Record] = Record.fetch_all(session)
        for idx, rec in enumerate(records):

            rec = rec.to_dataclass()

            start_time = rec.datetime_start
            duration = self.convert_seconds_to_str(rec.sec_duration)
            experiment = get_experiment_by_schedule_id(rec.schedule_id)
            obj = get_object_by_schedule_id(rec.schedule_id)
            file_format = rec.file_format
            table_data.append([rec.id, idx + 1, start_time, duration, experiment, obj, file_format,])

        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=table_data)

        # update label Schedule
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

        # остановить и удалить задачи из расписания
        job = self.scheduler.get_job(job_id=str(schedule_data[0]))
        if job is not None:
            logger.debug(f"Удалено расписание из планировщика с индексом: {str(schedule_data[0])}")
            self.scheduler.remove_job(job_id=str(schedule_data[0]))

        # удалить (пометить) расписание из БД
        schedule = Schedule.find([Schedule.id==schedule_data[0]], session)
        schedule.soft_delete(session)

        self.update_content_table_schedule()
        logger.debug(f"Удалено расписание из базы данных с индексом: {str(schedule_data[0])}")
        logger.debug(f"Удалено расписание из таблицы с индексом: {str(schedule_data[0])}")

        # удалить записи для расписания в history
        soft_delete_records(schedule_data[0], session)

        self.update_content_table_history()
        logger.debug(f"Удалены записи для расписания с индексом: {str(schedule_data[0])}")

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

    def clicked_schedule(self):
        """ Обработчик двойного нажатия на строку в таблице Schedule """
        data = self.tableModelSchedule.get_selected_data()
        schedule_id = data[0]
        print(f"{schedule_id=}")


    def configuration_clicked(self):
        dlg = DlgConfiguration()
        dlg.signal_restore.connect(self.update_content_table_history)
        dlg.signal_restore.connect(self.update_content_table_schedule)
        ok = dlg.exec()

    def closeEvent(self, event, /):
        self.ble_manager.stop()

    # def _get_row_as_dict(self, table: QTableView, index: QModelIndex) -> dict:
    #     model = table.model()
    #     data: dict = {}
    #     for idx_col in range(model.columnCount()):
    #         key = model.headerData(idx_col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
    #         data[key] = model.index(index.row(), idx_col).data(Qt.ItemDataRole.DisplayRole)
    #     return data

class DlgConfiguration(QDialog, Ui_DlgMainConfig):

    signal_restore = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.pushButtonRecordRecovery.clicked.connect(self.restore)

        self.pushButtonOk.clicked.connect(self.close)
        self.pushButtonCancel.clicked.connect(self.close)

    @connection
    def restore(self, session):
        restore(session)
        self.signal_restore.emit()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    # window.show()
    app.exec()