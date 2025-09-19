import datetime
import logging
from uuid import UUID

from PySide6.QtCore import QModelIndex, QAbstractTableModel, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog, QAbstractItemView, QHeaderView
from sqlalchemy import insert, select, delete, update

# scheduler
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE, EXAMPLE_DATA_SCHEDULE, \
    EXAMPLE_DATA_HISTORY
from structure import DataSchedule
# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule
from tools.modview import GenericTableWidget

# database
from database import database
from models import Schedule

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        # create view for table Schedule and History
        self.tableModelSchedule = GenericTableWidget()
        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=EXAMPLE_DATA_SCHEDULE, )
        self.labelSchedule.setText(f"Расписание (всего: {len(EXAMPLE_DATA_SCHEDULE)})")

        self.tableModelHistory = GenericTableWidget()
        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=EXAMPLE_DATA_HISTORY)
        self.labelHistory.setText(f"История (всего записей: {len(EXAMPLE_DATA_HISTORY)})")

        # add tables
        self.verticalLayoutHistory.addWidget(self.tableModelHistory)
        self.verticalLayoutSchedule.addWidget(self.tableModelSchedule)

        self.pushButtonAddSchedule.clicked.connect(self.addSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        # ToDo: self.pushButtonDeleteSchedule.clicked.connect(self.deleteScheduleFromDB)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

        # self.updateContentTableSchedule()
        # self.updateContentTableHistory()

    # Schedule
    def addSchedule(self) -> None:
        logger.info("Adding a new schedule")

        experiments = set([data[0] for data in EXAMPLE_DATA_SCHEDULE])

        dlg = DlgCreateSchedule(experiments=experiments)
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule: DataSchedule = dlg.getSchedule()

            if schedule is None:
                logger.error("An error occurred while creating the schedule")
                return

            # add schedule into database
            with database.engine.connect() as conn:
                stmt = insert(Schedule).values(
                    experiment=schedule.experiment,
                    patient=schedule.patient,
                    device_sn=schedule.device_sn, device_model=schedule.device_model,
                    duration_sec=schedule.duration, interval_sec=schedule.interval,
                    last_record_time=None, next_record_time=schedule.start_datetime,
                    start_datetime=schedule.start_datetime, finish_datetime=schedule.finish_datetime,
                    file_format=schedule.file_format, sampling_rate=schedule.sampling_rate
                )
                conn.execute(stmt)
                conn.commit()

            # fill table Schedule
            # self.updateContentTableSchedule()

            logger.info("Schedule created successfully")

    def updateContentTableSchedule(self):
        logger.info("Set data in the Schedule table")
        table_data = []

        with database.engine.connect() as conn:
            stmt = select(
                Schedule.experiment,
                Schedule.patient,
                Schedule.device_sn, Schedule.device_model,
                Schedule.start_datetime, Schedule.finish_datetime,
                Schedule.file_format, Schedule.sampling_rate
            )
            result = conn.execute(stmt)
            conn.commit()

        for row in result:
            table_data.append([*row])
        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=table_data)

        # update label Schedule
        self.labelSchedule.setText(f"Расписание (всего: {len(table_data)})")

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

    def updateContentTableHistory(self):
        # update label History
        self.labelHistory.setText(f"История (всего: 0)")

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