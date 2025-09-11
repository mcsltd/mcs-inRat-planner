import logging


from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog

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
        if dlg.exec() == QDialog.accepted:
            dlg.exec()
        schedule = dlg.getSchedule()
        print(schedule)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()