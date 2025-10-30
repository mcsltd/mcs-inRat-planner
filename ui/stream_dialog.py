import time
import uuid
from threading import Thread

import numpy as np
import logging
from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QWidget
from pyqtgraph import PlotWidget, mkPen
from pyqtgraph.multiprocess import CanceledError

from resources.v1.wdt_monitor import Ui_FormMonitor

logger = logging.getLogger(__name__ )

class PlotSignal(PlotWidget):
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

        self.timebase_s = 10      # окно отображения сигнала
        self.fs = 1000

    def set_data(self, time: np.ndarray, ecg: np.ndarray):
        """ Отображение сигнала на графике """
        if time.shape != ecg.shape:
            logger.error("Время и сигнал ЭКГ имеют разную размерность")
            return

        max_len = self.timebase_s * self.fs
        if len(self.time) < max_len:
            self.time = np.append(self.time, time)
            self.ecg = np.append(self.ecg, ecg)
        else:
            self.time = np.append(self.time[len(time):], time)
            self.ecg = np.append(self.ecg[len(ecg):], ecg)

        self.plot_signal.setData(self.time, self.ecg)
        self.setXRange(self.time[0], self.time[-1])

    def clear_plot(self):
        """Очистка графика"""
        self.time = np.array([])
        self.ecg = np.array([])
        self.clear()

class BLESignalViewer(QDialog, Ui_FormMonitor):

    def __init__(self, device_name, device_id, fs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle(f"Просмотр сигнала с {device_name}")

        self.device_name = device_name
        self._device_id: UUID | None = device_id
        self.fs = fs

        self.plot = PlotSignal(self)
        self.verticalLayoutMonitor.addWidget(self.plot)

    def accept_signal(self, device_id: UUID, data: dict):
        """ Принять данные от устройства с device_id """
        if self._device_id is None:
            logger.debug("Идентификатор устройства не установлен")
            return

        if self._device_id != device_id:
            logger.debug("Идентификатор устройства не соответствует установленному")
            return

        time, ecg = None, None

        if "emg" in data:
            ecg = np.array(data["emg"])
        elif "ecg" in data:
            ecg = np.array(data["ecg"])
        else:
            raise ValueError("No ECG recording")

        if "timestamp" in data:
            time = np.linspace(data["timestamp"], data["timestamp"] + len(ecg) / self.fs, len(ecg))
        else:
            raise ValueError("No time recording")

        self.plot.set_data(time, ecg)

class DeviceMockup(QWidget):
    signal_data_received = Signal(UUID, dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sample_size = 32

        self._name = "EMG-SENS-XXXX"
        self._id = uuid.uuid4()
        self.fs = 1000

        self.thread = None

    def start(self):
        """ запуск генератора синусоидального сигнала через отдельный поток """
        self.thread = Thread(target=self._generate_signal)
        self.thread.start()

    def _generate_signal(self):

        try:
            while True:
                timestamp = time.time()
                time_array = np.linspace(timestamp, timestamp + self.sample_size / self.fs, self.sample_size)
                ecg_array = np.sin(2 * np.pi * 3 * time_array)

                data = {"timestamp": timestamp, "emg": ecg_array.tolist()}
                self.signal_data_received.emit(self._id, data)
                time.sleep(1 / self.fs * self.sample_size)
        except CanceledError:
            return


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    device = DeviceMockup()
    device.start()

    viewer = BLESignalViewer(device_name=device._name, device_id=device._id, fs=device.fs)
    device.signal_data_received.connect(viewer.accept_signal)
    viewer.show()

    app.exec()
