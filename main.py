import logging

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Signal
from sqlalchemy import insert

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

        self.fill_table_rat()
        self.fill_table_device()

        # self.tableViewSchedule.setModel()       # QTableView

        self.pushButtonAddRat.clicked.connect(self.show_dlg_input_rat)
        self.pushButtonAddDevice.clicked.connect(self.show_dlg_input_device)

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

    def _insert_rat_into_db(self, name: str):
        try:
            with database.engine.connect() as conn:
                stmt = insert(Rat).values(name=name)
                result = conn.execute(stmt)
                conn.commit()
        except Exception as exc:
                logger.error(f"Raise error when add rat in db: {exc}")

    def fill_table_rat(self):
        column_names = Rat().get_columns()
        self.model_rat = DataTableModel(column_names=column_names, parent=self)
        self.tableViewRat.setModel(self.model_rat)            # QTableView


    def fill_table_device(self):
        column_names = Device().get_columns()
        self.model_device = DataTableModel(column_names=column_names, parent=self)
        self.tableViewDevice.setModel(self.model_device)        # QTableView



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()