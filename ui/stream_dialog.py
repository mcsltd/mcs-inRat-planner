import time
import uuid
from threading import Thread

import numpy as np
import logging
from uuid import UUID

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QDialog, QWidget, QPushButton, QSpinBox, QLabel, QHBoxLayout
from pyqtgraph import PlotWidget, mkPen

from structure import ScheduleData

PATH_TO_ICON = "resources/v1/icon_app.svg"

from resources.v1.wdt_monitor import Ui_FormMonitor

logger = logging.getLogger(__name__ )


def format_duration(seconds: int) -> str:
    """ Преобразует секунды в читаемый формат (минуты, часы)."""
    if seconds < 60:
        return f"{seconds} с."
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes} мин. {remaining_seconds} с."
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours} ч. {minutes} мин. {remaining_seconds} с."


class TimebaseControlWidget(QWidget):
    """Виджет для управления timebase (окном отображения сигнала)"""

    timebase_changed = Signal(float)  # Сигнал при изменении timebase

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Метка
        label = QLabel("Окно отображения:")
        label.setFont(QFont("Arial", 10))

        # Спинбокс для выбора timebase
        self.timebase_spinbox = QSpinBox()
        self.timebase_spinbox.setRange(2, 10)  # от 1 до 10 секунд
        self.timebase_spinbox.setValue(10)  # значение по умолчанию
        self.timebase_spinbox.setSuffix(" с")
        self.timebase_spinbox.setFont(QFont("Arial", 10))
        self.timebase_spinbox.valueChanged.connect(self._on_timebase_changed)

        # Добавляем все в layout
        layout.addWidget(label)
        layout.addWidget(self.timebase_spinbox)

        self.setLayout(layout)

    def set_timebase(self, timebase_s: float):
        """Установить значение timebase"""
        self.timebase_spinbox.setValue(int(timebase_s))

    def get_timebase(self) -> float:
        """Получить текущее значение timebase"""
        return float(self.timebase_spinbox.value())

    def _on_timebase_changed(self, value: int):
        """Обработчик изменения значения в спинбоксе"""
        self.timebase_changed.emit(float(value))


class PlotSignal(PlotWidget):
    def __init__(self, fs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackground("w")
        self.setWindowIcon(QIcon(PATH_TO_ICON))
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
        self.fs = fs

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

        if self.time[-1] < self.timebase_s:
            self.setXRange(self.time[0], self.timebase_s)
        else:
            self.setXRange(self.time[-1] - self.timebase_s, self.time[-1])

    def set_timebase(self, timebase_s: float):
        """Установить новое значение timebase"""
        self.timebase_s = timebase_s
        # Обновляем отображение с новым timebase
        if len(self.time) > 0:
            if self.time[-1] < self.timebase_s:
                self.setXRange(self.time[0], self.timebase_s)
            else:
                self.setXRange(self.time[-1] - self.timebase_s, self.time[-1])

    def clear_plot(self):
        """Очистка графика"""
        self.time = np.array([])
        self.ecg = np.array([])
        self.clear()


class BLESignalViewer(QDialog, Ui_FormMonitor):

    def __init__(self, schedule_data: ScheduleData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle(f"Регистрация ЭКГ сигнала объекта \"{schedule_data.object.name}\"")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowIcon(QIcon(PATH_TO_ICON))

        self.schedule_data = schedule_data

        self.device_name = self.schedule_data.device.ble_name
        self._device_id: UUID | None = self.schedule_data.device.id
        self.fs = schedule_data.sampling_rate
        self.mock_time = None

        # Создаем график и виджет управления timebase
        self.plot = PlotSignal(parent=self, fs=self.fs)
        self.timebase_control = TimebaseControlWidget()

        # Подключаем сигнал изменения timebase
        self.timebase_control.timebase_changed.connect(self.plot.set_timebase)

        # Добавляем виджеты в layout
        self.verticalLayoutInfo.addWidget(self.timebase_control)
        self.verticalLayoutInfo.addStretch()
        self.verticalLayoutMonitor.addWidget(self.plot)

        self._load_info()

    def accept_signal(self, device_id: UUID, data: dict):
        """ Принять данные от устройства с device_id """

        if self._device_id is None:
            logger.debug("Идентификатор устройства не установлен")
            return

        if self._device_id != device_id:
            logger.debug("Идентификатор устройства не соответствует установленному")
            return

        if self.mock_time is None:
            self.mock_time = time.time()

        time_arr, ecg = None, None
        if "emg" in data:
            ecg = np.array(data["emg"])
        elif "ecg" in data:
            ecg = np.array(data["ecg"])
        else:
            raise ValueError("No ECG recording")

        if "timestamp" in data:
            time_arr = np.linspace(data["timestamp"], data["timestamp"] + len(ecg) / self.fs, len(ecg)) - self.mock_time
        else:
            raise ValueError("No time recording")

        if "timestamp" in data and "start_timestamp" in data:
            sec_duration = int(data["timestamp"] - data["start_timestamp"])
            format_time = format_duration(sec_duration)
            self.labelDurationValue.setText(format_time)

        self.plot.set_data(time_arr, ecg)

    def _load_info(self):
        """ Отображение информации о записи """
        self.labelExperimentValue.setText(self.schedule_data.experiment.name)
        self.labelDeviceValue.setText(self.schedule_data.device.ble_name)
        self.labelObjectValue.setText(self.schedule_data.object.name)
        self.labelDurationValue.setText(f"{self.schedule_data.sec_duration} с.")
        self.labelSamplingRateValue.setText(f"{self.schedule_data.sampling_rate} Гц")
        self.labelStartTimeValue.setText(f"{str(self.schedule_data.datetime_start)}")

        self.labelFormat.hide()
        self.labelFormatValue.hide()
        self.formLayout_5.removeWidget(self.labelFormat)
        self.formLayout_5.removeWidget(self.labelFormatValue)
        self.labelFormatValue.setText(self.schedule_data.file_format)



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
        except KeyboardInterrupt:
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
