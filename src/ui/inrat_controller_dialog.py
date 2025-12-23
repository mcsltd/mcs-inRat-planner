import asyncio
import logging
import os
import threading
import time

import numpy as np
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QFileDialog
from PySide6 import QtCore

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog
from bleak import BleakScanner, BLEDevice
from pyqtgraph import PlotWidget, mkPen, InfiniteLine

from config import SAVE_DIR
from device.inrat.constants import InRatDataRateEcg, Command, ScaleAccelerometer, EnabledChannels, EventType
from device.inrat.inrat import InRat
from device.inrat.structures import InRatSettings
from resources.v1.dlg_inrat_controller import Ui_DlgInRatController
from structure import ScheduleData
from tools.inrat_storage import InRatStorage
from util import convert_in_rat_sample_rate_to_str, seconds_to_label_time

SAMPLE_RATES = [("500 Гц", InRatDataRateEcg.HZ_500.value),
                ("1000 Гц", InRatDataRateEcg.HZ_1000.value),
                ("2000 Гц", InRatDataRateEcg.HZ_2000.value), ]

MODE = [("Деактивирован", Command.Deactivate),
        ("Активирован", Command.Activate)]


logger = logging.getLogger(__name__)

class DisplaySignal(PlotWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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

        self._markers = []

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

        self.plot_signal.setData(self.time, self.ecg, antialias=True, clipToView=True)

        if self.time[-1] < self.timebase_s:
            self.setXRange(self.time[0], self.timebase_s)
        else:
            self.setXRange(self.time[-1] - self.timebase_s, self.time[-1])


    def set_sampling_rate(self, sampling_rate: int):
        """ Установка частоты оцифровки """
        self.fs = sampling_rate
        logger.info(f"Установлен новая частота: {self.fs} Гц")

    def set_marker(self, pos, text):
        """ Add vertical line and text on the plot."""
        line = InfiniteLine(
            pos=pos, angle=90, pen=mkPen('gray', width=2, style=QtCore.Qt.PenStyle.DashLine),
            movable=False, label=text, labelOpts={'color': 'k', 'position': 0.1})
        self.addItem(line)
        self._markers.append(line)

    def clear_plot(self):
        """Очистка графика"""
        logger.debug("Очистка графика")
        self.time = np.array([])
        self.ecg = np.array([])

        for marker in self._markers:
            self.removeItem(marker)
        self.markers = []

        self.plot_signal.clear()

class InRatControllerDialog(QDialog, Ui_DlgInRatController):

    signal_start_recording = Signal()
    signal_stop_recording = Signal()
    signal_accept_data = Signal(object)

    def __init__(self, schedule_data: ScheduleData, parent = None,  *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)

        # backend
        self.schedule_data = schedule_data
        self.device: None | InRat = None
        self.storage = InRatStorage(
            path_to_save=SAVE_DIR,
            device_name=self.schedule_data.device.ble_name,
            object_name=self.schedule_data.object.name
        )
        self.start_acquisition_time = None

        self._settings = InRatSettings(
            DataRateEcg=InRatDataRateEcg.HZ_500.value, HighPassFilterEcg=0,
            FullScaleAccelerometer=ScaleAccelerometer.G_2.value, EnabledChannels=EnabledChannels.ECG,
            EnabledEvents=EventType.TEMP,
            ActivityThreshold=1
        )
        self._loop = None
        self.is_running = False

        # ui
        self.labelDeviceName.setText(str(self.schedule_data.device.ble_name))
        self.labelObjectName.setText(str(self.schedule_data.object.name))

        self.setWindowTitle(f"Ручной режим: {self.schedule_data.device.ble_name}")
        self.display = DisplaySignal(self)
        self.setup_combobox()
        self.verticalLayoutPlot.addWidget(self.display)
        self.lineEditSave.setText(self.storage.path_to_save)

        # timer
        self.recording_timer = QTimer()
        self.recording_timer.setInterval(1000)

        # signals
        self.recording_timer.timeout.connect(self._on_timeout_expired)
        self.pushButtonConnection.clicked.connect(self._device_connection)
        self.pushButtonDisconnect.clicked.connect(self._device_disconnection)
        self.pushButtonStart.clicked.connect(self._device_acquisition)
        self.pushButtonStop.clicked.connect(self._device_stop_acquisition)
        self.comboBoxSampleFreq.currentIndexChanged.connect(self._on_samplerate_changed)
        self.comboBoxMode.currentIndexChanged.connect(self._on_mode_changed)
        self.comboBoxFormat.currentIndexChanged.connect(self._on_format_changed)
        self.pushButtonSelectDirSave.clicked.connect(self._on_save_dir_changed)
        self.pushButtonShowRecords.clicked.connect(self._on_save_dir_clicked)
        self.pushButtonStartRecording.clicked.connect(self._start_recording)
        self.pushButtonStopRecording.clicked.connect(self._stop_recording)

    # настройка таймера обновления времени
    def _on_timeout_expired(self):
        """ Обработчик таймера записи сигнала """
        if self.storage.start_time is None:
            self.labelRTvalue.setText("00:00:00")
            return

        sec_crnt_time = int(time.time() - self.storage.start_time)
        label_time = seconds_to_label_time(sec_crnt_time)
        self.labelRTvalue.setText(label_time)

    # настройка параметров сохранения
    def _on_save_dir_changed(self):
        """ Изменение места сохранения, по умолчанию data/ble_device/"""
        logger.debug("Изменено место сохранения")

        path_to_save = QFileDialog.getExistingDirectory(
            self,
            "Выбор места сохранения",
            # self.storage.path_to_save,
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        self.storage.set_save_dir(path_to_save)
        self.lineEditSave.setText(path_to_save)

    def _on_save_dir_clicked(self):
        """ Обработка нажатия кнопки"""
        if os.name == 'nt':  # Windows
            os.system(f'start "" "{self.storage.path_to_save}"')
        elif os.name == 'posix':  # Linux, macOS
            os.system(f'open "{self.storage.path_to_save}"')

    # настройка выпадающих списков
    def setup_combobox(self):
        """ Настройка выпадающих списков """
        for data in SAMPLE_RATES:
            self.comboBoxSampleFreq.addItem(*data)

        for data in MODE:
            self.comboBoxMode.addItem(*data)

        self._set_default_sampling_rate()
        self._set_default_format()

    def _set_default_sampling_rate(self):
        """ Установка частоты по умолчанию из schedule_data """
        # установка частоты по умолчанию
        text_sample_rate = f"{self.schedule_data.sampling_rate} Гц"
        idx = self.comboBoxSampleFreq.findText(text_sample_rate)
        self.comboBoxSampleFreq.setCurrentIndex(idx)
        self._on_samplerate_changed()

    def _set_default_format(self):
        """ Установка частоты по умолчанию из schedule_data """
        # установка частоты по умолчанию
        text_format = self.schedule_data.file_format
        idx = self.comboBoxFormat.findText(text_format)
        self.comboBoxFormat.setCurrentIndex(idx)
        self._on_format_changed()

    def _on_samplerate_changed(self):
        """ Обработчик изменения частоты оцифровки """
        text_sr = self.comboBoxSampleFreq.currentText()
        value = self.comboBoxSampleFreq.currentData()

        self._settings.DataRateEcg = value
        logger.debug(f"В структуру настроек установлена частота {convert_in_rat_sample_rate_to_str(self._settings.DataRateEcg)}")
        self.display.set_sampling_rate(sampling_rate=int(text_sr.split()[0]))
        self.storage.set_sampling_rate(int(text_sr.split()[0]))

        logger.debug(f"Установлена частота: {text_sr}, {value}")

    def _on_mode_changed(self):
        """ Обработчик изменения режима и установка режима в устройство через асинхронную задачу """
        text_mode = self.comboBoxMode.currentText()
        value = self.comboBoxMode.currentData()

        future = asyncio.run_coroutine_threadsafe(self._set_device_mode(value), self._loop)
        logger.debug(f"Установлен режим: {text_mode}, {value}")

    def _set_mode_combobox(self, mode: int):
        """ Установка текущего режима установленного на устройстве """
        logger.debug(f"Текущий режим на {self.schedule_data.device.ble_name}: {mode}")
        if mode == 0:
            self.comboBoxMode.setCurrentIndex(0)
        elif mode == 1:
            self.comboBoxMode.setCurrentIndex(1)

    def _on_format_changed(self):
        """ Изменен формат сохранения сигналов """
        frmt = self.comboBoxFormat.currentText()
        self.storage.set_format(frmt)
        logger.info(f"Изменен формат записи на {frmt}")

    # асихронный цикл событий
    def _run_async_loop(self):
        """ Создание цикла событий для работы с устройством"""
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(True)
        asyncio.set_event_loop(self._loop)

        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()
        logger.debug(f"Создан цикл событий: {self._loop}")

    # установка статуса устройству - Activated/Deactivated
    async def _set_device_mode(self, mode: Command):
        """ Изменение режима у устройства - Activated/Deactivated"""
        if await self.device.set_status(mode):
            status = await self.device.get_status()
            self._set_mode_combobox(mode=status.Activated)
            return
        logger.error(f"Не удалось установить режим для устройства: {self.schedule_data.device.ble_name}")

        if mode == Command.Activate:
            self.comboBoxMode.setCurrentIndex(0)
        if mode == Command.Deactivate:
            self.comboBoxMode.setCurrentIndex(1)

    # соединение с устройством
    def _device_connection(self):
        """ Соединение с устройством через асинхронную задачу """
        logger.debug("Выполняется соединение с устройством")
        if self._loop is None:
            self._run_async_loop()

        future = asyncio.run_coroutine_threadsafe(
            self._device_connection_impl(),
            self._loop
        )

    async def _device_connection_impl(self):
        """ Соединение с устройством  """
        self.pushButtonConnection.setEnabled(False)

        device = await self._find_device()

        if device is None:
            logger.debug(f"Устройство {self.schedule_data.device.ble_name} не найдено")
            self.pushButtonConnection.setEnabled(True)
            return

        if await self._connect_device(device):
            status = await self.device.get_status()
            self._set_mode_combobox(mode=status.Activated)

            # активация при подключении устройства
            self.pushButtonStart.setEnabled(True)
            self.pushButtonDisconnect.setEnabled(True)
            # деактивация при подключении устройства
            self.comboBoxMode.setEnabled(True)
            self.comboBoxSampleFreq.setEnabled(True)
            self.pushButtonDisconnect.setEnabled(True)

        else:
            self.pushButtonConnection.setEnabled(True)

    async def _find_device(self) -> BLEDevice | None:
        """ Поиск устройства """
        logger.debug(f"Идёт поиск устройства: {self.schedule_data.device.ble_name}")
        ble_device = await BleakScanner.find_device_by_name(self.schedule_data.device.ble_name, timeout=5)

        if ble_device is None:
            return None

        logger.debug(f"Найдено устройство: {ble_device}")
        return ble_device

    async def _connect_device(self, device: BLEDevice) -> bool:
        """ Соединение с устройством """
        # соединение
        self.device = InRat(ble_device=device)
        if await self.device.connect(timeout=10):
            logger.debug(f"Выполнено соединение с устройством: {self.device.name}, {self.device.address}")
            return True
        return False

    # отключение устройства
    def _device_disconnection(self):
        """ Отсоединение от устройства через асинхронную задачу """
        logger.debug("Отсоединение от устройства")
        if self._loop is None:
            self._run_async_loop()

        future = asyncio.run_coroutine_threadsafe(
            self._disconnect_device(),
            self._loop
        )

    async def _disconnect_device(self):
        """ Отсоединение от устройства """
        if self.device is None:
            logger.error("В device установлено None")
            return

        if not self.device.is_connected:
            logger.warning("Устройство уже отключено")
            return

        await self.device.disconnect()

        # очистка графика
        self.display.clear_plot()

        # активация
        self.pushButtonConnection.setEnabled(True)
        # деактивация
        self.pushButtonDisconnect.setEnabled(False)
        self.pushButtonStart.setEnabled(False)
        self.pushButtonStop.setEnabled(False)
        self.comboBoxSampleFreq.setEnabled(False)
        self.comboBoxMode.setEnabled(False)
        self.device = None

    # запуск устройства
    def _device_acquisition(self):
        """ Запуск устройства для получения данных через асинхронную задачу"""
        logger.debug("Запущено соединение и запуск устройства")
        if self._loop is None:
            self._run_async_loop()

        self.display.clear_plot()
        future = asyncio.run_coroutine_threadsafe(self._start_data_acquisition_impl(), self._loop)

    async def _start_data_acquisition_impl(self):
        """ Запуск устройства для получения данных """
        if not self.device.is_connected:
            logger.error(f"Устройство {self.schedule_data.device.ble_name} не подключено")

        # активация
        self.pushButtonStop.setEnabled(True)
        # деактивация
        self.comboBoxMode.setEnabled(False)
        self.comboBoxSampleFreq.setEnabled(False)
        self.pushButtonDisconnect.setEnabled(False)

        await self._start_data_acquisition()

    async def _start_data_acquisition(self):
        """ Остановка получения данных"""
        if self.device is None or not self.device.is_connected:
            logger.debug(f"Устройство {self.schedule_data.device.ble_name} не найдено, либо не подключено")
            return

        data_queue = asyncio.Queue()
        logger.debug(f"{self.schedule_data.device.ble_name} запущен на частоте: {convert_in_rat_sample_rate_to_str(self._settings.DataRateEcg)}")
        if await self.device.start_acquisition(data_queue=data_queue, settings=self._settings):
            self.is_running = True
            # деактивация в режиме получения данных
            self.pushButtonStart.setEnabled(False)

            # активация
            self.pushButtonStop.setEnabled(True)
            self.comboBoxSampleFreq.setEnabled(False)
            self.pushButtonStartRecording.setEnabled(True)

            while self.is_running:
                try:
                    data = await asyncio.wait_for(data_queue.get(), timeout=1.0)

                    if self.start_acquisition_time is None and "start_timestamp" in data:
                        self.start_acquisition_time = data["start_timestamp"]

                    if "signal" in data and "timestamp" in data and "start_timestamp" in data and "counter" in data:
                        start_time = data["start_timestamp"]
                        signal = data["signal"]
                        time_arr = np.linspace(
                            start_time + len(data["signal"]) * (data["counter"] - 1) / self.display.fs,
                            start_time + len(data["signal"]) * data["counter"] / self.display.fs, len(signal)) - start_time

                        self.display.set_data(time=time_arr, signal=signal)
                        self.signal_accept_data.emit(signal)

                    if "event" in data:
                        if data["event"] == "Temp":
                            temp_in_cels = np.round(data["temp"] / 1000, 2)
                            self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text=f"{temp_in_cels} °С")
                        if data["event"] == "Activity":
                            self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text="Activity")
                        if data["event"] == "Orientation":
                            self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text="Orientation")
                        if data["event"] == "Freefall":
                            self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text="Freefall")

                    data_queue.task_done()

                except asyncio.TimeoutError:
                    continue

                except Exception as exp:
                    logger.error(f"Ошибка обработки данных с устройства {self.schedule_data.device.ble_name}, {exp}")
                    # await self._stop_data_acquisition_impl()
                    break

    # остановка устройства
    def _device_stop_acquisition(self):
        """ Остановка устройства через асинхронную задачу """
        if self._loop is None:
            self._run_async_loop()

        future = asyncio.run_coroutine_threadsafe(
            self._stop_data_acquisition_impl(),
            self._loop
        )

    async def _stop_data_acquisition_impl(self):
        """ Остановка получения данных с устройства """
        if not self.is_running:
            logger.debug(f"Получение данных с {self.schedule_data.device.ble_name} уже остановлено")
            return

        if await self.device.stop_acquisition():
            if self.storage.is_recording:
                self.pushButtonStopRecording.click()

            self.is_running = False
            self.start_acquisition_time = None

            # активация при остановке получения данных
            self.pushButtonDisconnect.setEnabled(True)
            self.pushButtonStart.setEnabled(True)
            self.comboBoxMode.setEnabled(True)
            self.comboBoxSampleFreq.setEnabled(True)

            # деактивация при остановке устройства
            self.pushButtonStop.setEnabled(False)
            self.pushButtonStartRecording.setEnabled(False)
            self.pushButtonStopRecording.setEnabled(False)

            logger.info(f"Остановлено получение данных с {self.schedule_data.device.ble_name}")

    # управление записью сигнала
    def _start_recording(self):
        """ Начало записи сигнала """
        logger.info("Начало записи сигнала")

        # запуск таймера
        self.recording_timer.start()

        # connect
        self.signal_start_recording.connect(self.storage.start_recording)
        self.signal_stop_recording.connect(self.storage.stop_recording)
        self.signal_accept_data.connect(self.storage.accept_data)

        self.signal_start_recording.emit()

        if self.start_acquisition_time is not None:
            self.display.set_marker(text="Запись начата", pos=time.time() - self.start_acquisition_time)

        # ui
        self.pushButtonStartRecording.setEnabled(False)
        self.comboBoxFormat.setEnabled(False)
        self.pushButtonStopRecording.setEnabled(True)

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

        if self.start_acquisition_time is not None:
            self.display.set_marker(text="Запись остановлена", pos=time.time() - self.start_acquisition_time)

        # ui
        self.pushButtonStartRecording.setEnabled(True)
        self.comboBoxFormat.setEnabled(True)
        self.pushButtonStopRecording.setEnabled(False)

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