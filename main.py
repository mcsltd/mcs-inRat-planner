import logging


from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QDialog
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView
from PySide6.QtCore import Qt
from sqlalchemy import insert, select, delete

# table model
from tools.modview import DataTableModel

# ui
from ui.v1.main_window import Ui_MainWindow

# database
from database import database
from widgets import DlgCreateSchedule

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        self.pushButtonAddSchedule.clicked.connect(self.createSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        # ToDo: self.pushButtonDeleteSchedule.clicked.connect(...)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

    def createSchedule(self):
        dlg = DlgCreateSchedule()
        dlg.exec()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()