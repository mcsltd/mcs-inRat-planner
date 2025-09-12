import datetime
import logging

from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog, QAbstractItemView, QHeaderView
from sqlalchemy import insert

from tools.modview import DataTableModel
# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule

# database
from database import database
from models import Schedule

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        # create view for table Schedule
        self.tableModelSchedule = DataTableModel(
            column_names=["№", "Имя объекта", "Серийный номер", "Частота", "Формат", "Длительность", "Интервал",],
            data=[]
        )
        self.tableViewSchedule.setModel(self.tableModelSchedule)
        self.tableViewSchedule.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableViewSchedule.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableViewSchedule.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

        # create view for table History
        self.tableModelHistory = DataTableModel(
            column_names=["№", "Начало записи", "Конец записи", "Статус", "Формат", "Частота",],
            data=[]
        )
        self.tableViewHistory.setModel(self.tableModelHistory)
        self.tableViewHistory.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableViewHistory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableViewHistory.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

        self.pushButtonAddSchedule.clicked.connect(self.createSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        # ToDo: self.pushButtonDeleteSchedule.clicked.connect(...)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

    def createSchedule(self) -> None:
        dlg = DlgCreateSchedule()
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule = dlg.getSchedule()
            self._addScheduleIntoDB(schedule)
            return

    def _addScheduleIntoDB(self, schedule: dict) -> None:
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
            conn.execute(stmt)
            conn.commit()
        return None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()