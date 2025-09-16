import datetime
import logging
from uuid import UUID

from PySide6.QtCore import QModelIndex, QAbstractTableModel, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog, QAbstractItemView, QHeaderView
from apscheduler.events import EVENT_JOB_EXECUTED, JobExecutionEvent, EVENT_JOB_ADDED
from sqlalchemy import insert, select, delete, update

# scheduler
from apscheduler.schedulers.qt import QtScheduler

from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE
from controller import Controller
# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule
from tools.modview import _DataTableModel as DataTableModel, GenericTableWidget

# database
from database import database
from models import Schedule

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        # create controller device
        self.controller = Controller()

        # create scheduler for qt application
        # self.scheduler = QtScheduler()
        # self.scheduler.start()
        # self.scheduler.add_listener(self.checkGoodResultExecuteJob, EVENT_JOB_EXECUTED)
        # self.scheduler.add_listener(self.updateTableHistory, EVENT_JOB_ADDED)
        # self.generateJobsFromDB()

        # create view for table Schedule
        self.tableModelSchedule = GenericTableWidget()
        self.tableModelSchedule.setData(
            data=[],
            description=DESCRIPTION_COLUMN_SCHEDULE
        )

        self.tableModelHistory = GenericTableWidget()
        self.tableModelHistory.setData(
            description=DESCRIPTION_COLUMN_HISTORY,
            data=[]
        )

        self.verticalLayoutHistory.addWidget(self.tableModelHistory)
        self.verticalLayoutSchedule.addWidget(self.tableModelSchedule)

        # create view for table History
        # self.tableModelHistory = DataTableModel(column_names=["№", "Начало записи", "Конец записи", "Cтатус", "Формат", "Частота"], data=[])
        # self.setupTableView(self.tableViewHistory, self.tableModelHistory)
        # self.updateTableSchedule()

        self.pushButtonAddSchedule.clicked.connect(self.createSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        self.pushButtonDeleteSchedule.clicked.connect(self.deleteScheduleFromDB)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

    def checkGoodResultExecuteJob(self, event: JobExecutionEvent):
        schedule_id = UUID(event.job_id)

        # update time in table Schedule: last_record_time = next_record_time, next_record_time = next_record_time + sec_duration + interval
        with database.engine.connect() as conn:
            # get current "next record time", "duration", "sec repeat interval"
            stmt = select(
                Schedule.next_record_time, Schedule.sec_duration, Schedule.sec_repeat_interval
            ).where(
                Schedule.id == schedule_id
            )
            next_record_time, duration, interval = conn.execute(stmt).first()

            # ToDo: change it later (process time !!!)
            if next_record_time < datetime.datetime.now():
                next_record_time = datetime.datetime.now()

            stmt = update(Schedule).where(
                Schedule.id == schedule_id
            ).values(
                last_record_time=next_record_time,
                next_record_time=next_record_time + datetime.timedelta(seconds=duration + interval)
            )
            conn.execute(stmt)
            conn.commit()

            # create new job for new next_record_time
            ...

    def updateTableHistory(self, event):
        print("Update table history")
        schedule_id = UUID(event.job_id)

        history_column = ["№", "Начало записи", "Конец записи", "Cтатус", "Формат", "Частота"]
        data = []
        with database.engine.connect() as conn:
            stmt = select(Schedule.sec_duration, Schedule.sec_repeat_interval, Schedule.next_record_time, Schedule.format, Schedule.sampling_frequency).where(Schedule.id == schedule_id)
            result = conn.execute(stmt)

            for idx, row in enumerate(result):
                duration = row[0]
                interval = row[1]
                start_time = row[2]
                finish_time = start_time + datetime.timedelta(seconds=duration)
                format = row[3]
                sample_rate = row[4]
                status = "Выполняется"

                data.append([idx, start_time, finish_time, status, format, sample_rate])

        self.tableModelSchedule = DataTableModel(column_names=history_column, data=data)
        self.setupTableView(self.tableViewSchedule, self.tableModelSchedule)

    def generateJobsFromDB(self):
        # get schedule data from db
        with database.engine.connect() as conn:
            stmt = select(Schedule)
            result = conn.execute(stmt)
            schedules = [dict(row._mapping) for row in result]

        # add schedule as job in QtScheduler
        for sched in schedules:
            start_time = sched["next_record_time"]

            if not isinstance(start_time, datetime.datetime):
                raise TypeError("Type is not datetime!")

            # ToDo: change it later
            if start_time < datetime.datetime.now():
                start_time = datetime.datetime.now()

            logger.debug(
                f"Add new job from table Schedule: "
                f"id={sched['id']}, start_time={sched['next_record_time']}, duration={sched['sec_duration']} sec"
            )
            # self.scheduler.add_job(
            #     func=self.controller.start_recording, trigger="date",
            #     args=(sched["device_sn"], sched['next_record_time'], sched["sec_duration"]),
            #     id=str(sched["id"]), run_date=start_time,
            # )


    def createSchedule(self) -> None:
        dlg = DlgCreateSchedule()
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule = dlg.getSchedule()

            if schedule is None:
                return

            schedule_id = self._addScheduleIntoDB(schedule)
            # for example
            # add job in schedule
            # self.scheduler.add_job(
            #     func=self.controller.start_recording, args=(schedule["start_time"], schedule["duration"]),
            #     trigger="date", id=schedule_id, run_date=schedule["start_time"],
            #     next_run_time=schedule["start_time"] + datetime.timedelta(seconds=schedule["duration"] + schedule["interval"])
            # )


    def _addScheduleIntoDB(self, schedule: dict) -> str:
        logger.debug(f"Add in DB new schedule: {schedule=}")
        with database.engine.connect() as conn:
            stmt = insert(Schedule).values(
                patient=schedule["patient_name"],
                device_sn=schedule["device_sn"],
                sec_duration=schedule["duration"],
                sec_repeat_interval=schedule["interval"],
                last_record_time=None,
                next_record_time=schedule["start_time"],
                format=schedule["format"],
                sampling_frequency=schedule["freq"]
            )
            res = conn.execute(stmt)
            schedule_id: UUID = res.inserted_primary_key
            conn.commit()
        self.updateTableSchedule()
        return str(schedule_id)

    def updateTableSchedule(self):
        data = []
        with database.engine.connect() as conn:
            stmt = select(
                Schedule.id,
                Schedule.patient, Schedule.device_sn,
                Schedule.sampling_frequency, Schedule.format,
                Schedule.sec_duration, Schedule.sec_repeat_interval
            )
            rows = conn.execute(stmt)
            for idx, row in enumerate(rows):
                data.append([idx + 1, *row])
        self.tableModelSchedule = DataTableModel(column_names=["№", "id", "Имя объекта", "Серийный номер", "Частота", "Формат", "Длительность", "Интервал", ], data=data)
        self.setupTableView(self.tableViewSchedule, self.tableModelSchedule)

    def deleteScheduleFromDB(self):
        index = self.tableViewSchedule.currentIndex()
        data = self._get_row_as_dict(self.tableViewSchedule, index)
        self.tableModelSchedule.removeRow(index.row(), index)
        with database.engine.connect() as conn:
            stmt = delete(Schedule).where(Schedule.id == data["id"])
            conn.execute(stmt)
            conn.commit()

    def _get_row_as_dict(self, table: QTableView, index: QModelIndex) -> dict:
        model = table.model()
        data: dict = {}
        for idx_col in range(model.columnCount()):
            key = model.headerData(idx_col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            data[key] = model.index(index.row(), idx_col).data(Qt.ItemDataRole.DisplayRole)
        return data

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()