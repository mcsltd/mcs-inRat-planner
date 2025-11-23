import asyncio
import numpy as np

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog
from pyqtgraph import PlotWidget, mkPen

from resources.v1.dlg_inrat_controller import Ui_DlgInRatController
from structure import ScheduleData


class DisplaySignal(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackground("w")
        self.setDisabled(True)

        pen = mkPen("k")
        font = QFont("Arial", 11)

        self.time = np.array([])
        self.ecg = np.array([])
        self.plot_signal = self.plot(self.time, self.ecg, pen=mkPen("b"))

        self.setLabel("left", "V (мкВ)", pen=mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время (с)", pen=mkPen(color='k'), font=font)
        for ax in ["bottom", "left"]:
            self.getAxis(ax).label.setFont(font)
            self.getAxis(ax).setPen(pen)
            self.getAxis(ax).setTextPen(pen)
            self.getAxis(ax).setTickPen(pen)
            self.getAxis(ax).setTickFont(font)

        self.timebase_s = 10  # окно отображения сигнала


class InRatControllerDialog(QDialog, Ui_DlgInRatController):

    def __init__(self, schedule_data: ScheduleData, parent = None,  *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)
        self.schedule_data = schedule_data

        self.setWindowTitle(f"Ручной контроль устройства: {self.schedule_data.device.ble_name}")

        self.plot = DisplaySignal(parent=self)
        self.device = None
        self._loop = None

        self.verticalLayoutPlot.addWidget(self.plot)

        self.pushButtonStart.clicked.connect(self._connect_and_start_data_acquisition)
        self.pushButtonStop.clicked.connect(self._stop_data_acquisition)

    def _run_async_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    async def _connect_and_start_data_acquisition(self):
        ...

    async def _stop_data_acquisition(self):
        ...

    async def _disconnect_device(self):
        ...

    def closeEvent(self, arg__1, /):
        self._disconnect_device()
        if self._loop is not None:
            self._loop.close()
