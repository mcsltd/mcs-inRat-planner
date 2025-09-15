import datetime
import logging

from PySide6.QtCore import QModelIndex, QAbstractTableModel, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog, QAbstractItemView, QHeaderView
from sqlalchemy import insert, select, delete

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
        self.setupTableView(self.tableViewSchedule, self.tableModelSchedule)

        # create view for table History
        self.tableModelHistory = DataTableModel(
            column_names=["№", "Начало записи", "Конец записи", "Статус", "Формат", "Частота",],
            data=[]
        )
        self.setupTableView(self.tableViewHistory, self.tableModelHistory)
        self.updateTableSchedule()

        self.pushButtonAddSchedule.clicked.connect(self.createSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        self.pushButtonDeleteSchedule.clicked.connect(self.deleteScheduleFromDB)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

    def setupTableView(self, tableView: QTableView, tableModel: QAbstractTableModel):
        tableView.setModel(tableModel)
        tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        tableView.hideColumn(1)

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
        self.updateTableSchedule()
        return None

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
        self.tableModelSchedule = DataTableModel(
            column_names=["№", "id", "Имя объекта", "Серийный номер", "Частота", "Формат", "Длительность", "Интервал", ],
            data=data
        )
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