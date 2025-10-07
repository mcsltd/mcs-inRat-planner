from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QDialog
from pyqtgraph import PlotWidget, mkPen


from ui.v1.wdt_monitor import Ui_FormMonitor

class Display(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        font = QFont()
        font.setPointSize(12)

        # label
        self.setLabel("left", "V (мкВ)", pen=mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время (с)", pen=mkPen(color='k'), font=font)

        self.setBackground("w")
        self.setDisabled(True)



class SignalMonitor(QDialog, Ui_FormMonitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.display = Display(self)
        self.verticalLayoutMonitor.addWidget(self.display)

    def load_data(self):
        """ Загрузка сохраненных данных из файлов """
        pass