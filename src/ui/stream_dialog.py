import time
import uuid

from threading import Thread

import numpy as np
import logging
from uuid import UUID

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QDialog, QWidget, QSpinBox, QLabel, QHBoxLayout, QFrame, QApplication
from pyqtgraph import PlotWidget, mkPen

from structure import ScheduleData
from resources.wdt_monitor import Ui_FormMonitor

from resources.frm_online_control_plot import Ui_FrmOnlineControlPane

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


class ControlParamDisplay(Ui_FrmOnlineControlPane, QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        speed = [("12.5 мм/c", 12.5), ("25 мм/c", 25), ("50 мм/c", 50), ("100 мм/c", 100)]
        for v, d in speed:
            self.comboBoxSpeed.addItem(v, d)
        self.comboBoxSpeed.setCurrentIndex(0)

        voltage = [("0.3 мВ", 0.3 * 1e-3), ("0.5 мВ", 0.5 * 1e-3), ("1 мВ", 1 * 1e-3), ("1.5 мВ", 1.5 * 1e-3), ("2 мВ", 2 * 1e-3)]
        for v, d in voltage:
            self.comboBoxEcgLimit.addItem(v, d)
        self.comboBoxEcgLimit.setCurrentIndex(0)

        self.checkBoxDynamicRange.setChecked(True)
        self.checkBoxDynamicRange.clicked.connect(self.on_dynamic_range_clicked)

    def on_dynamic_range_clicked(self, checked: bool):
        """ обработка выбора динамического масштабирования """
        if not checked:
            self.comboBoxEcgLimit.setEnabled(True)
            self.comboBoxEcgLimit.activated.emit(1)
        else:
            self.comboBoxEcgLimit.setEnabled(False)

    def disable(self):
        """ отключение интерфейса """
        self.comboBoxEcgLimit.setDisabled(True)
        self.comboBoxSpeed.setDisabled(True)
        self.checkBoxDynamicRange.setDisabled(True)

    def enable(self):
        """ отключение интерфейса """
        self.comboBoxSpeed.setEnabled(True)
        self.checkBoxDynamicRange.setEnabled(True)
        if not self.checkBoxDynamicRange.isChecked():
            self.comboBoxEcgLimit.setEnabled(True)


class PlotSignal(PlotWidget):
    def __init__(self, fs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackground("w")
        self.setDisabled(True)

        pen = mkPen("k")
        font = QFont("Arial", 11)

        self.time = np.array([])
        self.ecg = np.array([])
        self.plot_signal = self.plot(pen=mkPen(color=(255, 0, 0), width=1.5))
        self.y_max, self.y_min = None, None

        self.setLabel("left", "ЭКГ", units="V", pen=mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время", units="s", pen=mkPen(color='k'), font=font)
        for ax in ["bottom", "left"]:
            self.getAxis(ax).label.setFont(font)
            self.getAxis(ax).setPen(pen)
            self.getAxis(ax).setTextPen(pen)
            self.getAxis(ax).setTickPen(pen)
            self.getAxis(ax).setTickFont(font)

        # виджет для контроля параметров графика
        self._control_pane = ControlParamDisplay()
        self._control_pane.comboBoxSpeed.activated.connect(self.set_speed)
        self._control_pane.comboBoxEcgLimit.activated.connect(self.set_limit)
        self._control_pane.checkBoxDynamicRange.clicked.connect(self.disable_limit)
        self._control_pane.enable() # активация интерфейса

        self.timebase_s = 10      # окно отображения сигнала
        self.fs = fs

    @property
    def control_pane(self) -> ControlParamDisplay:
        return self._control_pane

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

        self.plot_signal.setData(self.time, self.ecg, antialias=False, clipToView=True)

        if self.time[-1] < self.timebase_s:
            self.setXRange(self.time[0], self.timebase_s, padding=0)
        else:
            self.setXRange(self.time[-1] - self.timebase_s, self.time[-1], padding=0)

        # отображение по оси напряжения
        if not self.y_max and not self.y_min:
            if len(self.ecg) > 0:
                data_min = self.ecg.min()
                data_max = self.ecg.max()
                if data_max > data_min:
                    padding = (data_max - data_min) * 0.05
                    self.setYRange(data_min - padding, data_max + padding)
        else:
            self.setYRange(self.y_min, self.y_max)

    def set_speed(self):
        """ установка значения скорости прорисовки """
        speed = self._control_pane.comboBoxSpeed.currentData()

        # расчёт масштаба времени
        pixels_per_mm = QApplication.primaryScreen().physicalDotsPerInch() / 25.4
        width_mm = self.width() / pixels_per_mm
        timebase = int(width_mm / speed)

        self.timebase_s = timebase
        # Обновляем отображение с новым timebase
        if len(self.time) > 0:
            if self.time[-1] < self.timebase_s:
                self.setXRange(self.time[0], self.timebase_s)
            else:
                self.setXRange(self.time[-1] - self.timebase_s, self.time[-1])

    def set_limit(self):
        """ настройка отображаемого диапазона по оси Y """
        value = self._control_pane.comboBoxEcgLimit.currentData()
        self.y_max = value
        self.y_min = -value

    def disable_limit(self, state):
        """ отключения лимита отображения сигнала """
        if state:
            self.y_max, self.y_min = None, None

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
        self.setWindowFlags(Qt.Window)

        self.schedule_data = schedule_data

        self.device_name = self.schedule_data.device.ble_name
        self._device_id: UUID | None = self.schedule_data.device.id
        self.fs = schedule_data.sampling_rate
        self.mock_time = None
        self._last_data_timestamp = None

        # Создаем график и виджет управления timebase
        self.plot = PlotSignal(parent=self, fs=self.fs)

        # Добавляем виджеты в layout
        self.verticalLayoutInfo.addWidget(self.plot.control_pane)
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
            self.mock_time = data["start_timestamp"]

        if self._last_data_timestamp is None:
            self._last_data_timestamp = data["start_timestamp"]

        time_arr, signal = None, None
        if "signal" in data:
            signal = np.array(data["signal"])
        elif "event" in data:
            return
        else:
            raise ValueError("No signal recording")

        if "start_time" in data:
            time_arr = np.linspace(self._last_data_timestamp, self._last_data_timestamp + len(signal) / self.fs, len(signal)) - self.mock_time
            self._last_data_timestamp = self._last_data_timestamp + len(signal) / self.fs
        else:
            raise ValueError("No time recording")

        if "start_time" in data and "start_timestamp" in data:
            sec_duration = int(data["start_time"] - data["start_timestamp"])
            format_time = format_duration(sec_duration)
            self.labelDurationValue.setText(format_time)

        self.plot.set_data(time_arr, signal)


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

    def resizeEvent(self, arg__1, /):
        self.plot.set_speed()
