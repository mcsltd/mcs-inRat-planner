import datetime
import logging

from PyQt6.QtCore import QModelIndex
from PySide6.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QTableView, QHeaderView
from PySide6.QtCore import Signal, Qt, QAbstractTableModel
from sqlalchemy import insert, select, delete

from tools.modview import DataTableModel

# ui
from ui.main_window import Ui_MainWindow

# database
from database import database
from models import Device, Rat, Base, Schedule
from widgets import DlgInputDevice, DlgInputRat, DlgInputSchedule, Task

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat")

        # setup tables
        self.fill_table_rat()
        self.fill_table_device()
        self.update_table_schedules()
        self.tableViewRat.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableViewDevice.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableViewSchedule.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # setup stretch column on visible space table widget
        self.tableViewRat.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableViewDevice.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableViewSchedule.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.tableViewRat.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tableViewDevice.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tableViewSchedule.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

        # self.tableViewSchedule.setModel()       # QTableView

        # control rat
        self.pushButtonAddRat.clicked.connect(self.show_dlg_input_rat)
        self.pushButtonDeleteRat.clicked.connect(self._delete_rat_from_db)

        # control device
        self.pushButtonAddDevice.clicked.connect(self.show_dlg_input_device)
        self.pushButtonDeleteDevice.clicked.connect(self._delete_device_from_db)

        # control schedules
        self.pushButtonCreateTask.clicked.connect(self.show_dlg_input_task)
        self.pushButtonDeleteTask.clicked.connect(self._delete_schedule_from_db)

    def show_dlg_input_task(self) -> None:
        devices: dict = dict()
        rats: dict = dict()

        # ToDo: separate on functions
        # for devices
        for idx_row in range(self.tableViewDevice.model().rowCount()):
            index = self.tableViewDevice.model().index(idx_row, 0)
            data = self._get_row_as_dict(self.tableViewDevice, index)
            devices.update({data["name"]: data["id"]})

        # for rats
        for idx_row in range(self.tableViewRat.model().rowCount()):
            index = self.tableViewRat.model().index(idx_row, 0)
            data = self._get_row_as_dict(self.tableViewRat, index)
            rats.update({data["name"]: data["id"]})

        dlg = DlgInputSchedule(devices=devices, rats=rats)
        dlg.signal_insert.connect(self._insert_task_into_db)
        dlg.exec()

    def show_dlg_input_rat(self):
        dlg = DlgInputRat()
        dlg.signal_insert.connect(self._insert_rat_into_db)
        dlg.exec()

    def show_dlg_input_device(self):
        dlg = DlgInputDevice()
        dlg.signal_insert.connect(self._insert_device_into_db)
        dlg.exec()

    def _insert_device_into_db(self, name: str, serial: str, model: str):
        try:
            with database.engine.connect() as conn:
                stmt = insert(Device).values(name=name, serial=serial, model=model)
                result = conn.execute(stmt)
                conn.commit()
        except Exception as exc:
            logger.error(f"Raise error when add device in db: {exc}")
        finally:
            self.fill_table_device()

    def _insert_rat_into_db(self, name: str):
        try:
            with database.engine.connect() as conn:
                stmt = insert(Rat).values(name=name)
                result = conn.execute(stmt)
                conn.commit()
        except Exception as exc:
                logger.error(f"Raise error when add rat in db: {exc}")
        finally:
            self.fill_table_rat()

    def _insert_task_into_db(self, task: Task):
        logger.debug(f"Insert task into db: {task}")

        with database.engine.connect() as conn:
            stmt = insert(Schedule).values(
                sec_recording_duration=task.recording_duration,
                sec_repeat_time=task.repeat_time,
                last_recording_time=None,
                next_recording_time=None,
                id_device=task.device,
                id_rat=task.rat,
            )
            conn.execute(stmt)
            conn.commit()
        self.update_table_schedules()


    def _get_row_as_dict(self, table: QTableView, index: QModelIndex) -> dict:
        model = table.model()

        data: dict = {}
        for idx_col in range(model.columnCount()):
            key = model.headerData(idx_col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            data[key] = model.index(index.row(), idx_col).data(Qt.ItemDataRole.DisplayRole)
        return data

    def _delete_rat_from_db(self) -> None:
        index = self.tableViewRat.currentIndex()
        data = self._get_row_as_dict(self.tableViewRat, index)
        self.model_rat.removeRow(index.row(), index)
        with database.engine.connect() as conn:
            stmt = delete(Rat).where(Rat.id==data["id"])
            conn.execute(stmt)
            conn.commit()

    def _delete_device_from_db(self) -> None:
        index = self.tableViewDevice.currentIndex()
        data = self._get_row_as_dict(self.tableViewDevice, index)
        self.model_device.removeRow(index.row(), index)
        with database.engine.connect() as conn:
            stmt = delete(Device).where(Device.id==data["id"])
            conn.execute(stmt)
            conn.commit()

    def _delete_schedule_from_db(self) -> None:
        index = self.tableViewSchedule.currentIndex()
        data = self._get_row_as_dict(self.tableViewSchedule, index)
        self.model_schedule.removeRow(index.row(), index)
        with database.engine.connect() as conn:
            stmt = delete(Schedule).where(Schedule.id == data["id"])
            conn.execute(stmt)
            conn.commit()

    def fill_table_rat(self):
        arraydata = []
        column_names = Rat().get_columns()
        # get rats from db
        with database.engine.connect() as conn:
            stmt = select(Rat.id, Rat.name)
            for idx, row in enumerate(conn.execute(stmt)):
                arraydata.append([idx + 1, *row])
        self.model_rat = DataTableModel(column_names=column_names, data=arraydata, parent=self)
        self.tableViewRat.setModel(self.model_rat)            # QTableView
        self.tableViewRat.hideColumn(1)

    def fill_table_device(self):
        arraydata = []
        column_names = Device().get_columns()
        # get devices from db
        with database.engine.connect() as conn:
            stmt = select(Device.id, Device.name, Device.serial, Device.model)
            for idx, row in enumerate(conn.execute(stmt)):
                arraydata.append([idx + 1, *row])
        self.model_device = DataTableModel(column_names=column_names, data=arraydata, parent=self)
        self.tableViewDevice.setModel(self.model_device)        # QTableView
        self.tableViewDevice.hideColumn(1)

    def update_table_schedules(self):
        arraydata = []

        with database.engine.connect() as conn:
            stmt = select(
                Schedule.id,
                Schedule.sec_recording_duration, Schedule.sec_repeat_time,
                Schedule.last_recording_time, Schedule.next_recording_time,
                Rat.name, Device.name
            ).join(Device, Device.id == Schedule.id_device).join(Rat, Rat.id == Schedule.id_rat)
            for idx, row in enumerate(conn.execute(stmt)):
                arraydata.append([idx + 1, *row])

        self.model_schedule = DataTableModel(
            # columns - ["№", "id", "duration", "repeat time", "last recording time", "next recording time", "device", "rat"]
            column_names=Schedule().get_columns(),
            data=arraydata
        )
        self.tableViewSchedule.setModel(self.model_schedule)
        self.tableViewSchedule.hideColumn(1)



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()