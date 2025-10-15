import datetime
import logging


from asyncio import run

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog, QMessageBox

# scheduler
from apscheduler.schedulers.qt import QtScheduler

from ble_manager import BLEManager
# table
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE, RecordStatus
# from device.main import create_task_recording
from monitor import SignalMonitor
from structure import ScheduleData, RecordData
from ui.v1.dlg_main_config import Ui_DlgMainConfig

# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule
from tools.modview import GenericTableWidget

# database
from db.queries import add_schedule, add_device, add_object, add_record, \
    select_all_records, select_all_schedules, get_count_records, get_count_error_records, \
    get_object_by_schedule_id, get_experiment_by_schedule_id, delete_schedule, delete_records_by_schedule_id, \
    update_record_by_id, get_path_by_record_id

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        # init ble manager
        self.ble_manager = BLEManager()

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
        self.ble_manager.signal_stop_acquisition.connect(self.accept_signal)
        self.ble_manager.signal_error_recording.connect(self.handler_error_recording)

        # tables
        self.tableModelHistory.doubleClicked.connect(self.run_monitor)

        # buttons
        self.pushButtonAddSchedule.clicked.connect(self.add_schedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        self.pushButtonDeleteSchedule.clicked.connect(self.delete_schedule)
        self.actionSettings.triggered.connect(self.configuration_clicked)
        self.actionExit.triggered.connect(self.close)

        self.pushButtonDownloadRecords.setDisabled(True)
        self.pushButtonUpdateSchedule.setDisabled(True)

        # загрузить в таблицы данные
        self.update_content_table_history()
        self.update_content_table_schedule()

    def init_jobs(self):
        """ Метод инициализирующий задачи по записи ЭКГ """
        logger.info("Инициализация задач записи ЭКГ...")

        schedules = select_all_schedules()
        for job in schedules:

            if datetime.datetime.now() >= job.datetime_finish:
                logger.debug(f"Время действия расписания истекло: {job.datetime_finish} для {job.id}")
                return

            self.create_job(job, start_time=job.datetime_start)

    def create_job(self, schedule, start_time: datetime.datetime):
        """ Создание задачи для расписания"""
        logger.debug(
            f"Создана задача: {str(schedule.id)};"
            f" запланированное время старта: {start_time.replace(microsecond=0)};"
            f" длительность записи: {schedule.sec_duration}"
        )
        self.scheduler.add_job(
            self.create_record,
            args=(schedule, start_time),
            trigger="interval",
            seconds=schedule.sec_interval,
            id=str(schedule.id),
            next_run_time=start_time,
        )

    def create_record(self, schedule: ScheduleData, start_time: datetime.datetime):
        logger.debug(f"Начало записи данных: {start_time} по расписанию {schedule.id}")

        # добавление в базу данных информации о начале записи
        rec_d = RecordData(
            schedule_id=schedule.id,
            datetime_start=start_time,
            sec_duration=schedule.sec_duration,
            status=RecordStatus.IN_PROCESS.value,
            file_format=schedule.file_format,
            sampling_rate=schedule.sampling_rate,
        )
        record_id = add_record(rec_d)

        # обновить отображение данных в таблице Records
        self.update_content_table_history()
        run(self.ble_manager.start_recording(schedule, record_id))


    # Schedule
    def add_schedule(self) -> None:
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
            object_id = add_object(schedule.object)
            logger.info(f"Добавлен объект: id={object_id}")

            # обработка для повторного добавления устройства
            # add device in db
            device_id = add_device(schedule.device)
            logger.info(f"Добавлено устройство: id={device_id}")

            # add schedule in db
            schedule_id = add_schedule(schedule=schedule)
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

    def update_content_table_schedule(self):
        logger.info("Обновление всех данных в таблице \"Расписание\"")
        table_data = []

        schedules = select_all_schedules()
        for schedule in schedules:

            schedule_id = schedule.id
            experiment_name = schedule.experiment.name
            start_datetime = schedule.datetime_start
            finish_datetime = schedule.datetime_finish
            obj = schedule.object.name
            device = schedule.device.ble_name
            status = "Ожидание"
            interval = self.convert_seconds_to_str(schedule.sec_interval)
            duration = self.convert_seconds_to_str(schedule.sec_duration)
            all_records_time = 0
            all_records = get_count_records(schedule.id)
            error_record = get_count_error_records(schedule.id)
            params = f"{schedule.file_format}; {schedule.sampling_rate} Гц"

            table_data.append([schedule_id, experiment_name,start_datetime,finish_datetime,obj,device,status,interval,duration,all_records_time,all_records,error_record,params,])

        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=table_data)
        # update label Schedule
        self.labelSchedule.setText(f"Расписание (всего: {len(table_data)})")

    def update_content_table_history(self) -> None:
        logger.info("Обновление всех данных в таблице \"Записи\"")

        table_data = []
        records = select_all_records()
        for idx, rec in enumerate(records):
            start_time = rec.datetime_start
            duration = self.convert_seconds_to_str(rec.sec_duration)
            experiment = get_experiment_by_schedule_id(rec.schedule_id)
            obj = get_object_by_schedule_id(rec.schedule_id)
            file_format = rec.file_format
            table_data.append([rec.id, idx + 1, start_time, duration, experiment, obj, file_format,])

        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=table_data)

        # update label Schedule
        self.labelHistory.setText(f"Записей (всего: {len(table_data)})")

    def update_schedule(self) -> None:
        """ Обработчик кнопки изменения расписаний """
        ...

    def delete_schedule(self) -> None:
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
        delete_schedule(schedule_id=schedule_data[0])  # ToDo: не удалять из бд
        self.update_content_table_schedule()
        logger.debug(f"Удалено расписание из базы данных с индексом: {str(schedule_data[0])}")
        logger.debug(f"Удалено расписание из таблицы с индексом: {str(schedule_data[0])}")

        # удалить записи для расписания в history
        delete_records_by_schedule_id(schedule_id=schedule_data[0]) # ToDo: не удалять из бд
        self.update_content_table_history()
        logger.debug(f"Удалены записи для расписания с индексом: {str(schedule_data[0])}")

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

    def accept_signal(self, schedule, record_id, path_to_file):
        """ Приём данных о завершении записи сигнала с устройства """
        update_record_by_id(record_id, path_to_file, status=RecordStatus.OK.value)
        logger.debug(f"Update path in record with id {record_id}")


    def _get_row_as_dict(self, table: QTableView, index: QModelIndex) -> dict:
        model = table.model()
        data: dict = {}
        for idx_col in range(model.columnCount()):
            key = model.headerData(idx_col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            data[key] = model.index(index.row(), idx_col).data(Qt.ItemDataRole.DisplayRole)
        return data

    def handler_error_recording(self, schedule: ScheduleData, record_id, status):
        """ Обработка ошибки записи сигнала """
        update_record_by_id(record_id=record_id, status=status)
        reply = QMessageBox.warning(
            self, "Ошибка записи",
            f"Возникла ошибка записи с устройства {schedule.device.ble_name}",
            QMessageBox.StandardButton.Ok
        )

    def configuration_clicked(self):
        dlg = DlgConfiguration()
        ok = dlg.exec()


class DlgConfiguration(QDialog, Ui_DlgMainConfig):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.pushButtonOk.clicked.connect(self.close)
        self.pushButtonCancel.clicked.connect(self.close)


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