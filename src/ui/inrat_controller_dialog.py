import asyncio
import contextlib
import logging
import os
import threading
import time
import pyqtgraph as pg

import numpy as np
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtWidgets import QVBoxLayout, QProgressBar, QSizePolicy, QLabel, \
    QHBoxLayout, QSpacerItem, QDialogButtonBox, QFrame, QMessageBox, QApplication
from PySide6 import QtCore

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog
from bleak import BleakScanner, BLEDevice
from pyqtgraph import PlotWidget, mkPen, InfiniteLine

from device.inrat.constants import Pkt
from device.inrat.inrat import inRat
from resources.dlg_inrat_controller import Ui_DlgInRatController
from resources.frm_online_control_device import Ui_FrmOnlineControlDevice
from resources.frm_online_control_plot import Ui_FrmOnlineControlPane
from resources.frm_online_control_recording import Ui_FrmOnlineControlRecording
from structure import ScheduleData
from tools.inrat_storage import InRatStorage
from util import seconds_to_label_time

from structure import RecordData

from config import app_data

SAMPLE_RATES = [("500", 500),
                ("1000", 1000),
                ("2000", 2000)]


logger = logging.getLogger(__name__)


class ControlParamDisplay(Ui_FrmOnlineControlPane, QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        speed = [("12.5 мм/c", 12.5), ("25 мм/c", 25), ("50 мм/c", 50), ("100 мм/c", 100)]
        for v, d in speed:
            self.comboBoxSpeed.addItem(v, d)
        self.comboBoxSpeed.setCurrentIndex(0)

        # gain = [("5 мм/мВ", 5*1e-3), ("10 мм/мВ", 10*1e-3), ("20 мм/мВ", 20*1e-3), ("100 мм/c", 100*1e-3)]
        # for v, d in gain:
        #     self.comboBoxGain.addItem(v, d)
        # self.comboBoxGain.setCurrentIndex(1)
        # self.comboBoxGain.setDisabled(True)

class DisplaySignal(PlotWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setBackground("w")
        self.setDisabled(True)

        pen = mkPen("k")
        font = QFont("Arial", 11)
        self.plot_signal = self.plot(pen=pg.mkPen(color=(255, 0, 0), width=1.5))

        # data
        self.fs = 500
        self.max_timebase = 60
        self.timebase = 10
        self.dt = 1 / self.fs
        self.ecg_buffer = np.zeros(int(self.max_timebase * self.fs))
        self.time_buffer = np.arange(0, self.max_timebase, self.dt)
        # переменные для управления отображением
        self.buffer_filled = False  # флаг заполнения буфера
        self.current_position = 0  # текущая позиция для заполнения буфера


        self.setLabel("left", "ЭКГ", units="V", pen=mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время", units="s", pen=mkPen(color='k'), font=font)
        for ax in ["bottom", "left"]:
            self.getAxis(ax).label.setFont(font)
            self.getAxis(ax).setPen(pen)
            self.getAxis(ax).setTextPen(pen)
            self.getAxis(ax).setTickPen(pen)
            self.getAxis(ax).setTickFont(font)

        self._markers = []
        self.pending_update = False
        self._control_pane = ControlParamDisplay()
        self._control_pane.comboBoxSpeed.activated.connect(self.set_timebase)
        self.set_timebase()

    @property
    def control_panel(self):
        return self._control_pane

    def set_timebase(self):
        """ настройка масштаба времени """
        speed = self._control_pane.comboBoxSpeed.currentData()
        # расчёт масштаба времени
        pixels_per_mm = QApplication.primaryScreen().physicalDotsPerInch() / 25.4
        width_mm = self.width() / pixels_per_mm

        self.timebase = int(width_mm / speed)
        # self.update_plot()
        logger.info(f"Изменен масштаб по оси времени: {self.timebase} секунд")

    def set_sampling_rate(self, sampling_rate: int):
        """ Установка частоты оцифровки """
        self.fs = sampling_rate
        logger.info(f"Установлен новая частота: {self.fs} Гц")

    def set_marker(self, pos: float | None, text: str):
        """ Add vertical line and text on the plot."""
        if not pos:
            pos = self.time_buffer[self.current_position]
        line = InfiniteLine(
            pos=pos, angle=90, pen=mkPen('gray', width=2, style=QtCore.Qt.PenStyle.DashLine),
            movable=False, label=text, labelOpts={'color': 'k', 'position': 0.1})
        self.addItem(line)
        self._markers.append(line)

    def set_data(self, ecg: dict):
        """ добавление данных сигнала в буфер """
        signal, counter = ecg["signal"], ecg["counter"]
        if not self.buffer_filled:
            # вставка данных в незаполненный буфер
            if self.current_position + Pkt.SamplesCountEcg < len(self.ecg_buffer):
                self.ecg_buffer[self.current_position:self.current_position + Pkt.SamplesCountEcg] = signal
                self.current_position += Pkt.SamplesCountEcg
            else:
                offset = len(self.ecg_buffer) - self.current_position
                self.ecg_buffer[self.current_position:] = signal[:offset]
                signal = signal[offset:]
                self.buffer_filled = True

        # вставка данных в заполненный буфер
        if self.buffer_filled and len(signal) != 0:
            self.ecg_buffer = np.roll(self.ecg_buffer, -len(signal))
            self.ecg_buffer[-len(signal):] = signal
            self.time_buffer += len(signal) * self.dt

        self.pending_update = True

    def update_plot(self):
        """Обновление графика по таймеру"""
        if not self.pending_update:
            return

        if not self.buffer_filled:
            end_idx = self.current_position
            start_idx = 0

            if end_idx > self.timebase * self.fs:
                start_idx = end_idx - int(self.timebase * self.fs)
        else:
            end_idx = len(self.ecg_buffer)
            start_idx = end_idx - int(self.timebase * self.fs)
        visible_time = self.time_buffer[start_idx:end_idx]
        visible_ecg = self.ecg_buffer[start_idx:end_idx]

        # установка данных из буфера на дисплей
        self.plot_signal.setData(visible_time, visible_ecg)

        # отображение по оси времени
        if not self.buffer_filled and end_idx <= self.timebase * self.fs:
            self.setXRange(0, self.timebase, padding=0)
        else:
            current_time = visible_time[-1] if len(visible_time) > 0 else 0
            self.setXRange(current_time - self.timebase, current_time, padding=0)

        # отображение по оси напряжения
        if len(visible_ecg) > 0:
            data_min = visible_ecg.min()
            data_max = visible_ecg.max()
            if data_max > data_min:
                padding = (data_max - data_min) * 0.05
                self.setYRange(data_min - padding, data_max + padding)

        self.replot()
        self.pending_update = False

    def clear_plot(self):
        """Очистка графика"""
        # очистка графика от сигнала
        self.plot_signal.setData(np.array([]), np.array([]))  # clear signal
        self.plot_signal.clear()

        # очистка графика от маркеров
        for marker in self._markers:
            self.removeItem(marker)
        self._markers = []

        # сброс данных
        self.max_timebase = 60
        self.timebase = 10
        self.dt = 1 / self.fs
        self.ecg_buffer = np.zeros(int(self.max_timebase * self.fs))
        self.time_buffer = np.arange(0, self.max_timebase, self.dt)
        self.buffer_filled = False  # флаг заполнения буфера
        self.current_position = 0  # текущая позиция для заполнения буфера


class FrmOnlineControlDevice(QFrame, Ui_FrmOnlineControlDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        for sr in SAMPLE_RATES:
            self.comboBoxSampleFreq.addItem(*sr)

    def set_state_connected(self):
        """ ui для состояния остановки """
        self.pushButtonConnect.setEnabled(False)
        self.pushButtonDisconnect.setEnabled(True)
        self.pushButtonStart.setEnabled(True)
        self.pushButtonStop.setEnabled(False)
        self.comboBoxSampleFreq.setEnabled(True)
        self.checkBoxActivated.setEnabled(True)

    def set_state_disconnected(self):
        """ ui для состояния, когда устройство отсоединено """
        self.pushButtonConnect.setEnabled(True)
        self.pushButtonDisconnect.setEnabled(False)
        self.pushButtonStart.setEnabled(False)
        self.pushButtonStop.setEnabled(False)
        self.comboBoxSampleFreq.setEnabled(False)
        self.checkBoxActivated.setEnabled(False)

    def set_state_acquisition(self):
        """ ui для состояния, когда устройство старт """
        self.pushButtonConnect.setEnabled(False)
        self.pushButtonDisconnect.setEnabled(True)
        self.pushButtonStart.setEnabled(False)
        self.pushButtonStop.setEnabled(True)
        self.comboBoxSampleFreq.setEnabled(False)
        self.checkBoxActivated.setEnabled(False)

    def reset(self):
        """ сбор настроек """
        self.checkBoxActivated.setChecked(False)

class FrmOnlineControlRecording(Ui_FrmOnlineControlRecording, QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        for f in ["WFDB", "EDF"]:
            self.comboBoxFormat.addItem(f)


class InRatControllerDialog(QDialog, Ui_DlgInRatController):

    signal_start_recording = Signal()
    signal_stop_recording = Signal()
    signal_record_saved = Signal(object)

    signal_show_dialog = Signal()
    signal_close_dialog = Signal()

    signal_info_dialog = Signal(str)
    signal_accept_data = Signal(object)

    def __init__(self, schedule_data: ScheduleData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.Window)
        self.setupUi(self)

        # backend
        self.schedule_data = schedule_data
        self.device: None | inRat = None
        self.storage = InRatStorage(
            path_to_save=app_data.path_to_data, device_name=self.schedule_data.device.ble_name,
            object_name=self.schedule_data.object.name, experiment_name=self.schedule_data.experiment.name,
            schedule_id=self.schedule_data.id
        )
        self.start_acquisition_time = None

        self._loop = None
        self.is_running = False

        # ui
        self.labelExperimentName.setText(str(self.schedule_data.experiment.name))
        self.labelObjectName.setText(str(self.schedule_data.object.name))
        self.labelDeviceName.setText(str(self.schedule_data.device.ble_name))

        self.setWindowTitle(f"Ручной режим: {self.schedule_data.device.ble_name}")
        self.display = DisplaySignal(self)
        self.verticalLayoutPlot.addWidget(self.display)

        # панель для управления inrat
        self.control_panel_device = FrmOnlineControlDevice()
        # панель для управления сохранением записей ЭКГ
        self.control_panel_recording = FrmOnlineControlRecording()

        # timer
        self.recording_timer = QTimer()
        self.recording_timer.setInterval(1000)

        # waiting dialog
        self.dlg_waiting_connection = WaitingDialog(name=self.schedule_data.device.ble_name, parent=self)
        self.signal_show_dialog.connect(self.dlg_waiting_connection.show)
        self.signal_close_dialog.connect(self.dlg_waiting_connection.close)

        # info dialog
        self.dlg_info_connection = InfoConnectionDialog(name=self.schedule_data.device.ble_name, parent=self)
        self.signal_info_dialog.connect(self.dlg_info_connection.show_dialog)

        # signals
        self.storage.signal_record_saved.connect(self._on_record_saved)
        self.recording_timer.timeout.connect(self._on_timeout_expired)

        # управление устройством
        self.control_panel_device.pushButtonConnect.clicked.connect(self._device_connection)
        self.control_panel_device.pushButtonDisconnect.clicked.connect(self._device_disconnection)
        self.control_panel_device.pushButtonStart.clicked.connect(self._device_start_acquisition)
        self.control_panel_device.pushButtonStop.clicked.connect(self._device_stop_acquisition)
        self.control_panel_device.comboBoxSampleFreq.currentIndexChanged.connect(self._on_samplerate_changed)
        self.control_panel_device.checkBoxActivated.clicked.connect(self._on_mode_changed)

        # сохранение
        self.control_panel_recording.comboBoxFormat.currentIndexChanged.connect(self._on_format_changed)
        self.control_panel_recording.pushButtonStartRecording.clicked.connect(self._start_recording)
        self.control_panel_recording.pushButtonStopRecording.clicked.connect(self._stop_recording)

        self.verticalLayout.insertWidget(2, self.control_panel_device)
        self.verticalLayout.insertWidget(3, self.display.control_panel)
        self.verticalLayout.insertWidget(4, self.control_panel_recording)
        self.verticalLayout.addStretch()

        # установка таймера для обновления графика
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.display.update_plot)
        self.update_timer.start(16)

        self.setup_combobox()

    # настройка таймера обновления времени
    def _on_timeout_expired(self):
        """ Обработчик таймера записи сигнала """
        if self.storage.start_time is None:
            self.control_panel_recording.labelRTValue.setText("00:00:00")
            return

        sec_crnt_time = int(time.time() - self.storage.start_time)
        label_time = seconds_to_label_time(sec_crnt_time)
        self.control_panel_recording.labelRTValue.setText(label_time)

    def _on_save_dir_clicked(self):
        """ Обработка нажатия кнопки"""
        if os.name == 'nt':  # Windows
            os.system(f'start "" "{self.storage.path_to_save}"')
        elif os.name == 'posix':  # Linux, macOS
            os.system(f'open "{self.storage.path_to_save}"')

    # настройка выпадающих списков
    def setup_combobox(self):
        """ Настройка выпадающих списков """
        self._set_default_sampling_rate()
        self._set_default_format()

    def _set_default_sampling_rate(self):
        """ Установка частоты по умолчанию из schedule_data """
        # установка частоты по умолчанию
        text_sample_rate = f"{self.schedule_data.sampling_rate}"
        idx = self.control_panel_device.comboBoxSampleFreq.findText(text_sample_rate)
        self.control_panel_device.comboBoxSampleFreq.setCurrentIndex(idx)

        value = self.control_panel_device.comboBoxSampleFreq.currentData()
        self.storage.set_sampling_rate(int(value))
        self._on_samplerate_changed()

    def _set_default_format(self):
        """ Установка частоты по умолчанию из schedule_data """
        # установка частоты по умолчанию
        text_format = self.schedule_data.file_format
        idx = self.control_panel_recording.comboBoxFormat.findText(text_format)
        self.control_panel_recording.comboBoxFormat.setCurrentIndex(idx)
        self._on_format_changed()

    def _on_samplerate_changed(self):
        """ Обработчик изменения частоты оцифровки """
        text_sr = self.control_panel_device.comboBoxSampleFreq.currentText()
        value = self.control_panel_device.comboBoxSampleFreq.currentData()

        if self.device:
            self.device.sampling_rate = value
            logger.debug(f"Для {self.device.name} установлена частота {value} Гц")
        self.display.set_sampling_rate(sampling_rate=int(value))
        self.storage.set_sampling_rate(int(value))
        logger.debug(f"Установлена частота: {text_sr}, {value}")

    def _on_mode_changed(self):
        """ Обработчик изменения режима и установка режима в устройство через асинхронную задачу """
        value: Qt.CheckState = self.control_panel_device.checkBoxActivated.checkState()
        if value is Qt.CheckState.Checked:
            _ = asyncio.run_coroutine_threadsafe(self.device.activate(True), self._loop)
            logger.debug(f"{self.device.name} - активировано")
        else:
            _ = asyncio.run_coroutine_threadsafe(self.device.activate(False), self._loop)
            logger.debug(f"{self.device.name} - деактивировано")

    def _set_state_activated(self, activated: bool):
        """ Установка текущего режима установленного на устройстве """
        if activated:
            logger.info(f"Устройство {self.schedule_data.device.ble_name}: активировано")
            self.control_panel_device.checkBoxActivated.setChecked(True)
        else:
            logger.info(f"Устройство {self.schedule_data.device.ble_name}: деактивировано")
            self.control_panel_device.checkBoxActivated.setChecked(False)

    def _on_format_changed(self):
        """ Изменен формат сохранения сигналов """
        frmt = self.control_panel_recording.comboBoxFormat.currentText()
        self.storage.set_format(frmt)
        logger.info(f"Изменен формат записи на {frmt}")

    # асинхронный цикл событий
    def _run_async_loop(self):
        """ Создание цикла событий для работы с устройством"""
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(True)
        asyncio.set_event_loop(self._loop)

        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()
        logger.debug(f"Создан цикл событий: {self._loop}")

    # соединение с устройством
    def _device_connection(self):
        """ Соединение с устройством через асинхронную задачу """
        logger.debug("Выполняется соединение с устройством")
        if self._loop is None:
            self._run_async_loop()

        future = asyncio.run_coroutine_threadsafe(self._device_connection_impl(), self._loop)

    async def _device_connection_impl(self):
        """ Соединение с устройством  """
        self.signal_show_dialog.emit()

        try:
            self.control_panel_device.pushButtonConnect.setEnabled(False)
            device = await self._find_device(timeout=5)

            if device is None:
                logger.debug(f"Устройство {self.schedule_data.device.ble_name} не найдено")
                self.control_panel_device.set_state_disconnected()
                return

            # соединение с устройством
            if await self._connect_device(device):
                self._set_state_activated(activated=self.device.is_activated)
                self._set_default_sampling_rate()

                # установка частоты
                self.device.sampling_rate = self.schedule_data.sampling_rate
                self.display.set_sampling_rate(int(self.device.sampling_rate))

                logger.debug(f"{self.device.name} установлена частота {self.device.sampling_rate} Гц")
                self.control_panel_device.set_state_connected()
                self.display.control_panel.comboBoxSpeed.setEnabled(True)

            else:
                self.control_panel_device.set_state_disconnected()
        except:
            pass
        finally:
            self.signal_close_dialog.emit()

            if not self.device or not self.device.is_connected:
                self.signal_info_dialog.emit(f"Не удалось подключиться к {self.schedule_data.device.ble_name}.\n"
                                             f"Повторите попытку подключения.")

    async def _find_device(self, timeout: float):
        """ поиск устройства за время равное timeout """
        async with BleakScanner() as scanner:
            with contextlib.suppress(asyncio.TimeoutError):
                async with asyncio.timeout(timeout):
                    async for ble_device, _ in scanner.advertisement_data():
                        if ble_device and ble_device.name == self.schedule_data.device.ble_name:
                            return ble_device
        return None

    async def _connect_device(self, device: BLEDevice) -> bool:
        """ Соединение с устройством """
        # соединение
        self.device = inRat(ble_device=device)
        if await self.device.connect(wait=10):
            logger.debug(f"Выполнено соединение с устройством: {self.device.name}, {self.device.address}")
            return True
        return False

    # отключение устройства
    def _device_disconnection(self):
        """ Отсоединение от устройства через асинхронную задачу """
        logger.debug("Отсоединение от устройства")
        if self._loop is None:
            self._run_async_loop()
        future = asyncio.run_coroutine_threadsafe(self._disconnect_device(), self._loop)

    async def _disconnect_device(self):
        """ Отсоединение от устройства """
        # очистка графика
        self.display.clear_plot()
        if self.device:
            await self.device.disconnect()
        self.control_panel_device.set_state_disconnected()
        self.control_panel_device.reset()
        self._set_default_sampling_rate()
        self.device = None
        self.display.control_panel.comboBoxSpeed.setEnabled(False)


    # запуск устройства
    def _device_start_acquisition(self):
        """ Запуск устройства для получения данных через асинхронную задачу"""
        logger.debug(f"Запуск {self.device.name} на регистрацию ЭКГ")
        if self._loop is None:
            self._run_async_loop()

        self.display.clear_plot()
        future = asyncio.run_coroutine_threadsafe(self._start_data_acquisition_impl(), self._loop)

    async def _start_data_acquisition_impl(self):
        """ Запуск устройства для получения данных """
        if not self.device.is_connected:
            logger.error(f"Устройство {self.device.name} не подключено")
            self._device_disconnection()
            return

        await self._start_data_acquisition()

    async def _start_data_acquisition(self):
        """ Остановка получения данных"""
        if self.device is None or not self.device.is_connected:
            logger.debug(f"Устройство {self.schedule_data.device.ble_name} не найдено, либо не подключено")
            return

        data_queue = asyncio.Queue()
        logger.debug(f"{self.schedule_data.device.ble_name} будет запущен на частоте {self.device.sampling_rate}")

        if await self.device.start_acquisition(data_queue=data_queue):
            self.start_acquisition_time = time.time()
            self.control_panel_device.set_state_acquisition()
            self.display.control_panel.comboBoxSpeed.setEnabled(True)

            self.display.clear_plot()
            self.display.set_timebase()


            self.is_running = True
            self.control_panel_recording.pushButtonStartRecording.setEnabled(True)

            while self.is_running:
                try:
                    data = await asyncio.wait_for(data_queue.get(), timeout=1.0)

                    if "signal" in data:
                        self.display.set_data(data)
                        signal = data["signal"]
                        self.signal_accept_data.emit(signal)

                    data_queue.task_done()

                except asyncio.TimeoutError:
                    continue

                except Exception as exp:
                    logger.error(f"Ошибка обработки данных с устройства {self.schedule_data.device.ble_name}, {exp}")
                    await self._stop_data_acquisition_impl()
                    break

        if not self.device.is_connected:  # обрыв соединения (происходит после команды получения данных)
            logger.error(f"Потеряно соединение с {self.device.name}!")
            self.signal_info_dialog.emit(
                f"Потеряно соединение с устройством {self.device.name}!\n"
                f"Повторите попытку подключения."
            )
            self._device_stop_acquisition()
            self._device_disconnection()
            self.control_panel_device.set_state_disconnected()
            return

    # остановка устройства
    def _device_stop_acquisition(self):
        """ Остановка устройства через асинхронную задачу """
        if self._loop is None:
            self._run_async_loop()
        future = asyncio.run_coroutine_threadsafe(self._stop_data_acquisition_impl(), self._loop)

    async def _stop_data_acquisition_impl(self):
        """ Остановка получения данных с устройства """
        if not self.is_running:
            logger.debug(f"Получение данных с {self.schedule_data.device.ble_name} уже остановлено")
            return

        await self.device.stop_acquisition()

        # остановка записи
        if self.storage.is_recording:
            self.control_panel_recording.pushButtonStopRecording.click()

        self.is_running = False
        self.start_acquisition_time = None

        # активация при остановке получения данных
        self.control_panel_device.set_state_connected()
        # self.display.control_panel.comboBoxSpeed.setEnabled(False)
        self.control_panel_recording.pushButtonStartRecording.setEnabled(False)
        self.control_panel_recording.pushButtonStopRecording.setEnabled(False)

        logger.info(f"Остановлено получение данных с {self.schedule_data.device.ble_name}")

    # управление записью сигнала
    def _start_recording(self):
        """ Начало записи сигнала """
        logger.info("Начало записи сигнала")
        self.storage.start_recording()

        # запуск таймера
        self.recording_timer.start()

        # connect
        self.signal_start_recording.connect(self.storage.start_recording)
        self.signal_stop_recording.connect(self.storage.stop_recording)
        self.signal_accept_data.connect(self.storage.accept_data)

        self.signal_start_recording.emit()
        self.display.set_marker(text="Запись начата", pos=time.time() - self.start_acquisition_time)

        # ui
        self.control_panel_recording.pushButtonStartRecording.setEnabled(False)
        self.control_panel_recording.comboBoxFormat.setEnabled(False)
        self.control_panel_recording.pushButtonStopRecording.setEnabled(True)

    def _stop_recording(self):
        """ Остановка записи сигнала """
        logger.info("Остановка записи сигнала")
        self.signal_stop_recording.emit()

        # остановка таймера
        self.recording_timer.stop()
        self._on_timeout_expired()

        # disconnect
        self.signal_start_recording.disconnect(self.storage.start_recording)
        self.signal_stop_recording.disconnect(self.storage.stop_recording)
        self.signal_accept_data.disconnect(self.storage.accept_data)

        if self.start_acquisition_time:
            self.display.set_marker(text="Запись остановлена", pos=time.time() - self.start_acquisition_time)
        else:
            self.display.set_marker(text="Запись остановлена", pos=None)

        # ui
        self.control_panel_recording.pushButtonStartRecording.setEnabled(True)
        self.control_panel_recording.comboBoxFormat.setEnabled(True)
        self.control_panel_recording.pushButtonStopRecording.setEnabled(False)

    def _on_record_saved(self, record_data: RecordData) -> None:
        self.signal_record_saved.emit(record_data)

    # остановка и закрытие окна
    def closeEvent(self, event, /):
        if self._loop is None or not self._loop.is_running():
            event.accept()
            return
        try:
            # отключение устройства и завершение задач
            future = asyncio.run_coroutine_threadsafe(
                self._safe_shutdown(),
                self._loop
            )
            # завершения с таймаутом
            future.result(timeout=5.0)

        except TimeoutError:
            logger.warning("Таймаут при завершении задач")
        except Exception as e:
            logger.error(f"Ошибка при завершении: {e}")
        finally:
            # останавка цикла событий
            if self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)

            # ожидание завершения потока
            if self._loop_thread and self._loop_thread.is_alive():
                self._loop_thread.join(timeout=3.0)
                if self._loop_thread.is_alive():
                    logger.warning("Поток цикла событий не завершился вовремя")

            # закрытие цикла
            if not self._loop.is_closed():
                self._loop.close()

            logger.debug("Цикл событий завершён")
            event.accept()

    async def _safe_shutdown(self):
        """Безопасное завершение всех операций"""
        try:
            # Сначала отключаем устройство
            await self._disconnect_device()

            # Затем завершаем все задачи
            await self._shutdown_async_tasks()

        except Exception as e:
            logger.error(f"Ошибка при безопасном завершении: {e}")

    async def _shutdown_async_tasks(self):
        """Корректное завершение всех асинхронных задач"""
        if not self._loop or not self._loop.is_running():
            return

        # отмена всех задач
        tasks = [task for task in asyncio.all_tasks(self._loop)
                 if not task.done()]

        if not tasks:
            return

        logger.debug(f"Отменяем {len(tasks)} активных задач")

        # отмена всех задач
        for task in tasks:
            task.cancel()

        # ожидание завершения задач с таймаутом
        try:
            await asyncio.wait(tasks, timeout=2.0)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"Ошибка при отмене задач: {e}")

    def resizeEvent(self, arg__1, /):
        self.display.set_timebase()

class WaitingDialog(QDialog):

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Поиск и подключение к {name}")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        font = QFont()
        font.setPointSize(10)

        self.setFixedSize(300, 150)
        layout = QVBoxLayout()

        self.label = QLabel(f"Идёт поиск и подключение к {name}...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(font)

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setRange(0, 0)

        self.progress.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)

        self.setLayout(layout)


class InfoConnectionDialog(QDialog):
    def __init__(self, name, parent):
        super().__init__(parent=parent)
        self.setWindowTitle(f"Информация о соединении с {name}")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setMinimumSize(300, 120)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        text_layout = QHBoxLayout()

        self.label = QLabel(
            f"Не удалось подключиться к {name}.\nПовторите попытку подключения."
        )
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)

        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        text_layout.addWidget(self.label)

        main_layout.addLayout(text_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)

        self.button_box.setFixedHeight(30)

        for button in self.button_box.buttons():
            button.setMinimumSize(40, 30)

        main_layout.addWidget(self.button_box)

    def show_dialog(self, text: None | str = None):
        if text:
            self.label.setText(text)
        self.show()

    def accept(self):
        super().accept()