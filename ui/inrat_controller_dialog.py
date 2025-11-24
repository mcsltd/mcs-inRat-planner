import asyncio
import logging
import threading

import numpy as np
from PySide6.QtCore import Signal

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog
from bleak import BleakScanner
from pyqtgraph import PlotWidget, mkPen
from sqlalchemy.util import await_only

from device.inrat.constants import InRatDataRateEcg, Command, ScaleAccelerometer, EnabledChannels, EventType
from device.inrat.inrat import InRat
from device.inrat.structures import InRatSettings
from resources.v1.dlg_inrat_controller import Ui_DlgInRatController
from structure import ScheduleData

SAMPLE_RATES = [("500 Гц", InRatDataRateEcg.HZ_500.value),
                ("1000 Гц", InRatDataRateEcg.HZ_1000.value),
                ("2000 Гц", InRatDataRateEcg.HZ_2000.value), ]

MODE = [("Деактивация", Command.Deactivate.value),
        ("Активация", Command.Activate.value)]


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

        self.timebase_s = 5  # окно отображения сигнала
        self.fs = 500

    def set_data(self, time: np.ndarray, signal: np.ndarray):
        """ Отображение сигнала на графике """
        if time.shape != signal.shape:
            logger.error("Время и сигнал ЭКГ имеют разную размерность")
            return

        max_len = self.timebase_s * self.fs
        if len(self.time) < max_len:
            self.time = np.append(self.time, time)
            self.ecg = np.append(self.ecg, signal)
        else:
            self.time = np.append(self.time[len(time):], time)
            self.ecg = np.append(self.ecg[len(signal):], signal)

        self.plot_signal.setData(self.time, self.ecg)

        if self.time[-1] < self.timebase_s:
            self.setXRange(self.time[0], self.timebase_s)
        else:
            self.setXRange(self.time[-1] - self.timebase_s, self.time[-1])

    def set_sampling_rate(self, sampling_rate: int):
        """ Установка частоты оцифровки """
        self.fs = sampling_rate
        logger.info(f"Установлен новая частота: {self.fs} Гц")

    def clear_plot(self):
        """Очистка графика"""
        self.time = np.array([])
        self.ecg = np.array([])
        self.clear()

class InRatControllerDialog(QDialog, Ui_DlgInRatController):

    def __init__(self, schedule_data: ScheduleData, parent = None,  *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)

        # backend
        self.schedule_data = schedule_data
        self.device: None | InRat = None
        self._settings = InRatSettings(
            DataRateEcg=InRatDataRateEcg.HZ_500.value,
            HighPassFilterEcg=0,
            FullScaleAccelerometer=ScaleAccelerometer.G_2.value,
            EnabledChannels=EnabledChannels.ECG,
            EnabledEvents=EventType.START | EventType.TEMP,
            ActivityThreshold=1
        )
        self._loop = None
        self.is_running = False

        # ui
        self.labelDeviceName.setText(str(self.schedule_data.device.ble_name))
        self.setWindowTitle(f"Ручной контроль устройства: {self.schedule_data.device.ble_name}")
        self.display = DisplaySignal(parent=self)
        self.setup_combobox()
        self.verticalLayoutPlot.addWidget(self.display)

        # signals
        self.pushButtonStart.clicked.connect(self._connect_and_start_data_acquisition)
        self.pushButtonStop.clicked.connect(self._stop_data_acquisition)
        self.comboBoxSampleFreq.currentIndexChanged.connect(self._on_samplerate_changed)
        self.comboBoxMode.currentIndexChanged.connect(self._on_mode_changed)

    def setup_combobox(self):
        """ Настройка выпадающих списков """
        for data in SAMPLE_RATES:
            self.comboBoxSampleFreq.addItem(*data)

        for data in MODE:
            self.comboBoxMode.addItem(*data)

        self.comboBoxMode.setEnabled(False)
        self.comboBoxSampleFreq.setEnabled(False)

    def _on_samplerate_changed(self):
        """ Обработчик изменения частоты оцифровки """
        text_sr = self.comboBoxSampleFreq.currentText()
        value = self.comboBoxSampleFreq.currentData()
        self.display.set_sampling_rate(sampling_rate=int(text_sr.split()[0]))
        logger.debug(f"Установлена частота: {text_sr}, {value}")

    def _on_mode_changed(self):
        """ Обработчик изменения режима """
        text_mode = self.comboBoxMode.currentText()
        value = self.comboBoxMode.currentData()
        logger.debug(f"Установлен режим: {text_mode}, {value}")

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

        # self.display.clear_plot()

        future = asyncio.run_coroutine_threadsafe(
            self._connect_and_start_data_acquisition_impl(),
            self._loop
        )

    async def _connect_and_start_data_acquisition_impl(self):
        self.pushButtonStart.setEnabled(False)

        await self._connect_device()
        await self._start_data_acquisition_device()

    async def _connect_device(self):
        """ Поиск и соединение с устройством """
        if self.device is not None and self.device.is_connected:
            logger.info(f"Устройство {self.schedule_data.device.ble_name} уже подключено")
            return

        logger.debug(f"Идёт поиск устройства: {self.schedule_data.device.ble_name}")

        # поиск
        ble_device = None
        try:
            ble_device = await asyncio.wait_for(BleakScanner.find_device_by_name(self.schedule_data.device.ble_name), timeout=10)
        except asyncio.TimeoutError:
            self.pushButtonStart.setEnabled(True)
            return
        logger.debug(f"Найдено устройство: {ble_device}")

        if ble_device is None:
            return

        # соединение
        self.device = InRat(ble_device=ble_device)
        if await self.device.connect(timeout=10):
            self.pushButtonStop.setEnabled(True)
            logger.debug(f"Выполнено соединение с устройством: {self.device.name}, {self.device.address}")
            return

        self.pushButtonStart.setEnabled(True)

    async def _start_data_acquisition_device(self):
        """ Остановка получения данны"""
        if self.device is None or not self.device.is_connected:
            logger.debug(f"Устройство {self.schedule_data.device.ble_name} не найдено, либо не подключено")
            return

        data_queue = asyncio.Queue()
        if await self.device.start_signal_acquisition(signal_queue=data_queue, settings=self._settings):
            self.is_running = True

            while self.is_running:
                try:
                    data = await asyncio.wait_for(data_queue.get(), timeout=1.0)

                    if (
                            "signal" in data and
                            "timestamp" in data and
                            "start_timestamp" in data and
                            "counter" in data
                    ):
                        start_time = data["start_timestamp"]
                        signal = data["signal"]
                        time_arr = np.linspace(
                            start_time + len(data["signal"]) * (data["counter"] - 1) / self.display.fs,
                            start_time + len(data["signal"]) * data["counter"] / self.display.fs, len(signal)) - start_time

                        self.display.set_data(time=time_arr, signal=signal)

                    data_queue.task_done()
                except asyncio.TimeoutError:
                    continue

                except Exception as exp:
                    logger.error(f"Ошибка обработки данных с устройства {self.schedule_data.device.ble_name}, {exp}")
                    await self._stop_data_acquisition_impl()
                    break

    def _stop_data_acquisition(self):
        logger.debug("Запущено соединение и запуск устройства")
        if self._loop is None:
            self._run_async_loop()

        future = asyncio.run_coroutine_threadsafe(
            self._stop_data_acquisition_impl(),
            self._loop
        )

    async def _stop_data_acquisition_impl(self):
        """ Остановка получения данных с устройства """
        if self.device is None or not self.device.is_connected:
            logger.debug("Устройство не найдено или не подключено")

        if not self.is_running:
            logger.debug(f"Получение данных с {self.schedule_data.device.ble_name} уже остановлено")
            return

        if await self.device.stop_acquisition():
            self.is_running = False
            logger.info(f"Остановлено получение данных с {self.schedule_data.device.ble_name}")
            self.pushButtonStart.setEnabled(True)
            self.pushButtonStop.setEnabled(False)
            return

    async def _disconnect_device(self):
        """ Отсоединение от устройства """
        if self.device is None or not self.device.is_connected:
            return

        await self.device.disconnect()
        self.pushButtonStop.setEnabled(False)
        self.pushButtonStart.setEnabled(True)
        logger.debug("Выполнено отсоединение от устройства")


    def closeEvent(self, arg__1, /):
        if self._loop is not None:
            future = asyncio.run_coroutine_threadsafe(
                self._disconnect_device(),
                self._loop
            )
            future.result(3)

            self._loop.stop()
            self._loop.close()


