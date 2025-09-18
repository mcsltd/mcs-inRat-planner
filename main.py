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

        # create view for table Schedule and History
        self.tableModelSchedule = GenericTableWidget()
        self.tableModelSchedule.setData(data=[], description=DESCRIPTION_COLUMN_SCHEDULE)
        self.tableModelHistory = GenericTableWidget()
        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=[])

        # add tables
        self.verticalLayoutHistory.addWidget(self.tableModelHistory)
        self.verticalLayoutSchedule.addWidget(self.tableModelSchedule)

        self.pushButtonAddSchedule.clicked.connect(self.addSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        # ToDo: self.pushButtonDeleteSchedule.clicked.connect(self.deleteScheduleFromDB)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

    # Schedule
    def addSchedule(self) -> None:
        logger.info("Adding a new schedule")
        dlg = DlgCreateSchedule()
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule = dlg.getSchedule()
            if schedule is None:
                return

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





    # def init_scheduler(self):
    #     # create controller device
    #     # self.controller = Controller()
    #     # create scheduler for qt application
    #     # self.scheduler = QtScheduler()
    #     # self.scheduler.start()
    #     # self.scheduler.add_listener(self.checkGoodResultExecuteJob, EVENT_JOB_EXECUTED)
    #     # self.scheduler.add_listener(self.updateTableHistory, EVENT_JOB_ADDED)
    #     # self.generateJobsFromDB()
    #     pass

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()