import asyncio
import logging
import threading

import numpy as np

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog
from bleak import BleakScanner
from pyqtgraph import PlotWidget, mkPen

from device.inrat.inrat import InRat
from resources.v1.dlg_inrat_controller import Ui_DlgInRatController
from structure import ScheduleData

logger = logging.getLogger(__name__)

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

        self.device: None | InRat = None
        self._loop = None
        self.plot = DisplaySignal(parent=self)

        self.verticalLayoutPlot.addWidget(self.plot)

        self.pushButtonStart.clicked.connect(self._connect_and_start_data_acquisition)
        self.pushButtonStop.clicked.connect(self._stop_data_acquisition)

    def _run_async_loop(self):
        """ Создание цикла событий для работы с устройством"""
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(True)
        asyncio.set_event_loop(self._loop)

        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()
        logger.debug(f"Создан цикл событий: {self._loop}")

    def _connect_and_start_data_acquisition(self):
        """ Соединение и запуск устройства через асинхронную задачу"""
        logger.debug("Запущено соединение и запуск устройства")
        if self._loop is None:
            self._run_async_loop()

        future = asyncio.run_coroutine_threadsafe(
            self._connect_and_start_data_acquisition_impl(),
            self._loop
        )
        self.pushButtonStart.setEnabled(False)

    async def _connect_and_start_data_acquisition_impl(self):
        await self._connect_device()
        await asyncio.sleep(3)
        await self._disconnect_device()

    async def _connect_device(self):
        """ Поиск и соединение с устройством """
        logger.debug(f"Идёт поиск устройства: {self.schedule_data.device.ble_name}")
        ble_device = None
        try:
            ble_device = await asyncio.wait_for(BleakScanner.find_device_by_name(self.schedule_data.device.ble_name), timeout=10)
        except asyncio.TimeoutError:
            self.pushButtonStart.setEnabled(True)
            return
        logger.debug(f"Найдено устройство: {ble_device}")

        if ble_device is None:
            return

        self.device = InRat(ble_device=ble_device)

        if await self.device.connect(timeout=10):
            self.pushButtonStop.setEnabled(True)
            logger.debug(f"Выполнено соединение с устройством: {self.device.name}, {self.device.address}")
            return
        self.pushButtonStart.setEnabled(True)

    async def _disconnect_device(self):
        """ Отсоединение от устройства """
        if self.device is None or not self.device.is_connected:
            return

        await self.device.disconnect()
        self.pushButtonStop.setEnabled(False)
        self.pushButtonStart.setEnabled(True)
        logger.debug("Выполнено отсоединение от устройства")

    def _stop_data_acquisition(self):
        ...

    def closeEvent(self, arg__1, /):
        if self._loop is not None:
            self._loop.stop()
            self._loop.close()
