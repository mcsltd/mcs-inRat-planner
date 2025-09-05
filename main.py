import logging

from PyQt6.QtCore import QModelIndex
from PySide6.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QTableView
from PySide6.QtCore import Signal, Qt, QAbstractTableModel
from sqlalchemy import insert, select, delete

from tools.modview import DataTableModel

# ui
from ui.main_window import Ui_MainWindow

# database
from database import database
from models import Device, Rat, Base
from widgets import DlgInputDevice, DlgInputRat


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat")

        # setup tables
        self.fill_table_rat()
        self.fill_table_device()
        self.tableViewRat.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableViewDevice.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # self.tableViewSchedule.setModel()       # QTableView

        self.pushButtonAddRat.clicked.connect(self.show_dlg_input_rat)
        self.pushButtonDeleteRat.clicked.connect(self._delete_rat_from_db)

        self.pushButtonAddDevice.clicked.connect(self.show_dlg_input_device)
        self.pushButtonDeleteDevice.clicked.connect(self._delete_device_from_db)

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

    def _get_row_as_dict(self, table: QTableView, index: QModelIndex):
        model = table.model()

        data = {}
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

    def _delete_device_from_db(self):
        index = self.tableViewDevice.currentIndex()
        data = self._get_row_as_dict(self.tableViewDevice, index)
        self.model_device.removeRow(index.row(), index)
        with database.engine.connect() as conn:
            stmt = delete(Device).where(Device.id==data["id"])
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


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()