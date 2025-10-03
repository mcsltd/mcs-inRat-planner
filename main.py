import datetime
import logging

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog

# scheduler
from apscheduler.schedulers.qt import QtScheduler

# table
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE, EXAMPLE_DATA_SCHEDULE, \
    EXAMPLE_DATA_HISTORY, RecordStatus
from structure import ScheduleData

# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule, DlgCreateExperiment
from tools.modview import GenericTableWidget

# database
from db.queries import get_experiments, add_schedule, get_schedules, add_device, add_object, add_experiment, add_record, \
    get_records, select_all_schedules


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        # init scheduler
        self.scheduler = QtScheduler()
        self.scheduler.start()
        # self.initJobs()

        # create view for table Schedule and History
        self.tableModelSchedule = GenericTableWidget()
        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=EXAMPLE_DATA_SCHEDULE, )
        self.labelSchedule.setText(f"Расписание (всего: {len(EXAMPLE_DATA_SCHEDULE)})")

        self.tableModelHistory = GenericTableWidget()
        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=EXAMPLE_DATA_HISTORY)
        self.labelHistory.setText(f"Записей (всего: {len(EXAMPLE_DATA_HISTORY)})")

        # add tables
        self.verticalLayoutHistory.addWidget(self.tableModelHistory)
        self.verticalLayoutSchedule.addWidget(self.tableModelSchedule)

        self.pushButtonAddExperiment.clicked.connect(self.addExperiment)
        self.pushButtonAddSchedule.clicked.connect(self.addSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        # ToDo: self.pushButtonDeleteSchedule.clicked.connect(self.deleteScheduleFromDB)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

        self.updateContentTableSchedule()
        self.updateContentTableHistory()

    # def initJobs(self):
    #     logger.debug("Initialize schedules")
    #
    #     # read schedules from db
    #     scheds = select_all_schedules()
    #     for sc in scheds:
    #         _  = 1
            # # set job for scheduling
            # self.scheduler.add_job(
            #     self.addRecord,
            #     trigger="interval",
            #     seconds=schedule.sec_interval,
            #     args=(schedule, schedule_id),
            #     id=str(schedule_id),
            #     next_run_time=time,
            # )

    def addRecord(self, schedule: ScheduleData, schedule_id):
        """ Start recording """
        logger.debug(f"get schedule: {schedule}")

        # set data about record in table
        duration = schedule.sec_duration
        self.tableModelHistory.setData(
            description=DESCRIPTION_COLUMN_HISTORY,
            data=[["0", str(datetime.datetime.now()), duration, schedule.experiment, schedule.patient, schedule.file_format]]
        )

        # set data about record in db
        add_record(
            start=datetime.datetime.now(),
            finish=datetime.datetime.now() + datetime.timedelta(seconds=schedule.sec_duration),
            sec_duration=duration,
            sampling_rate=schedule.sampling_rate,
            file_format=schedule.file_format,
            scheduled_id=schedule_id,
            status=RecordStatus.IN_PROCESS.value
        )

        # start recording data from device
        ...

    # Experiment
    def addExperiment(self) -> None:
        dlg = DlgCreateExperiment()
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            exp = dlg.getExperiment()
            logger.info(f"Add Object in DB: id={add_experiment(exp)}")
        return


    # Schedule
    def addSchedule(self) -> None:
        logger.info("Adding a new schedule")

        experiments = get_experiments()
        dlg = DlgCreateSchedule(experiments=experiments)
        code = dlg.exec()

        if code == QDialog.DialogCode.Accepted:
            schedule: ScheduleData = dlg.getSchedule()

            if schedule is None:
                logger.error("An error occurred while creating the schedule")
                return

            # add object in db
            object_id = add_object(name=schedule.object.name)
            logger.info(f"Add Object in DB: id={object_id}")

            # add device in db
            device_id = add_device(sn=schedule.device.serial_number, model=schedule.device.model)
            logger.info(f"Add Device in DB: id={device_id}")

            # add schedule in db
            schedule_id = add_schedule(schedule=schedule, experiment_id=schedule.experiment.id, device_id=device_id, object_id=object_id)
            logger.info(f"Add Schedule in DB: id={schedule_id}")

            # ToDo: temprorary check time
            time = schedule.datetime_start
            if time <= datetime.datetime.now():
                time = datetime.datetime.now()

            # # set job for scheduling
            # self.scheduler.add_job(
            #     self.addRecord,
            #     trigger="interval",
            #     seconds=schedule.sec_interval,
            #     args=(schedule, schedule_id),
            #     id=str(schedule_id),
            #     next_run_time=time,
            # )

            # fill table Schedule
            self.updateContentTableSchedule()
            logger.info("Schedule created successfully")


    def updateContentTableSchedule(self):
        logger.info("Set data in the Schedule table")
        table_data = []

        result = get_schedules()

        # ToDo: rewrite it
        for row in result:
            column_1_5 = row[:5]
            status = ("None",)
            column_7_8 = row[7:8]
            column_9_11 = 4 * (0,)
            params = "; ".join([str(v) for v in row[-2:]]) + " Гц"
            data = list(column_1_5 + status + column_7_8 + column_9_11)
            data.append(params)
            table_data.append(data)

        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=table_data)
        # update label Schedule
        self.labelSchedule.setText(f"Расписание (всего: {len(table_data)})")

    def updateContentTableHistory(self):
        logger.debug("Update content in table history.")

        # update label History
        self.labelHistory.setText(f"История (всего: 0)")
        records = get_records()
        # for row in records:
        #     print(f"{row=}")


    def updateSchedule(self) -> None:
        logger.info("The contents of the Schedule table have been updated")
        pass

    def deleteSchedule(self) -> None:
        logger.info("Deleting a schedule")
        pass

    # History
    def updateTableHistory(self):
        logger.info("The contents of the History table have been updated")
        pass



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
    # window.show()
    app.exec()