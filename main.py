from PySide6.QtWidgets import QMainWindow, QApplication, QHeaderView

from tools.modview import DataTableModel
# ui
from ui.main_window import Ui_MainWindow

# database
from database import database
from models import Device, Rat, Base


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat")

        self.fill_table_rat()
        self.fill_table_device()

        # self.tableViewSchedule.setModel()       # QTableView


    def fill_table_rat(self):
        column_names = Rat().get_columns()
        self.model_rat = DataTableModel(column_names=column_names, parent=self)
        self.tableViewRat.setModel(self.model_rat)            # QTableView


    def fill_table_device(self):
        column_names = Device().get_columns()
        self.model_device = DataTableModel(column_names=column_names, parent=self)
        self.tableViewDevice.setModel(self.model_device)        # QTableView



if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()