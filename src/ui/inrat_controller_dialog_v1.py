import asyncio
import copy
import logging
import os
import queue
import threading
import time
from asyncio import Future, AbstractEventLoop

import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QProgressBar, QSizePolicy, QLabel, \
    QHBoxLayout, QSpacerItem, QDialogButtonBox

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog
from bleak import BleakScanner, BLEDevice

from src.display import DisplayScope
from src.resources.dlg_inrat_controller import Ui_DlgInRatController
from src.structure import ScheduleData
from src.device.device import inRatDevice

logger = logging.getLogger(__name__)


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
        self.setupUi(self)

        # backend
        self.schedule_data = schedule_data

        self._loop: AbstractEventLoop | None = None
        self._run_async_loop()

        self.is_running = False
        self.device: inRatDevice = inRatDevice(loop=self._loop)
        self.device.device_connected.connect(self._on_device_connected)
        self.device.device_disconnected.connect(self._on_device_disconnected)
        self.device.device_started.connect(self._on_device_started)
        self.device.device_stopped.connect(self._on_device_stopped)

        # ui
        self.labelExperimentName.setText(str(self.schedule_data.experiment.name))
        self.labelObjectName.setText(str(self.schedule_data.object.name))
        self.labelDeviceName.setText(str(self.schedule_data.device.ble_name))

        self.setWindowTitle(f"Ручной режим: {self.schedule_data.device.ble_name}")
        self.display = DisplayScope(self)
        self.verticalLayoutPlot.addWidget(self.display)

        # waiting dialog
        self.dlg_waiting_connection = WaitingDialog(name=self.schedule_data.device.ble_name, parent=self)
        self.signal_show_dialog.connect(self.dlg_waiting_connection.show)
        self.signal_close_dialog.connect(self.dlg_waiting_connection.close)

        # info dialog
        self.dlg_info_connection = InfoConnectionDialog(name=self.schedule_data.device.ble_name, parent=self)
        self.signal_info_dialog.connect(self.dlg_info_connection.show_dialog)

        self.pushButtonConnection.clicked.connect(self.device_discovery_and_connect)
        self.pushButtonDisconnect.clicked.connect(self.device_disconnect)
        self.pushButtonStart.clicked.connect(self.device_start_acquisition)
        self.pushButtonStop.clicked.connect(self.device_stop_acquisition)

        self.device.add_receiver(self.display)

    # асинхронный цикл событий
    def _run_async_loop(self):
        """ Создание цикла событий для работы с устройством"""
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(True)
        asyncio.set_event_loop(self._loop)

        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()
        logger.debug(f"Создан цикл событий: {self._loop}")


    # поиск и соединение с устройством
    def device_discovery_and_connect(self):
        """ Соединение с устройством через асинхронную задачу """
        logger.debug("Выполняется соединение с устройством")
        if self._loop is None:
            self._run_async_loop()

        self.signal_show_dialog.emit()
        # поиск устройств
        future = asyncio.run_coroutine_threadsafe(self._find_device(), self._loop)
        future.add_done_callback(self._on_device_connect)

    def _on_device_connect(self, future: Future):
        """ Обработка нахождения устройства """
        ble_device = future.result()
        self.signal_close_dialog.emit()

        if ble_device is None:
            self.signal_info_dialog.emit(f"Устройство {self.schedule_data.device.ble_name} не найдено!")
            return

        self.pushButtonConnection.setEnabled(False)
        self.device.process_connect(ble_device)

    def _on_device_connected(self):
        self.pushButtonDisconnect.setEnabled(True)
        self.pushButtonConnection.setEnabled(False)
        self.pushButtonStart.setEnabled(True)
        self.pushButtonStop.setEnabled(False)
    def _on_device_disconnected(self):
        self.pushButtonDisconnect.setEnabled(False)
        self.pushButtonConnection.setEnabled(True)
        self.pushButtonStart.setEnabled(False)
        self.pushButtonStop.setEnabled(False)
    def _on_device_stopped(self):
        self.pushButtonDisconnect.setEnabled(True)
        self.pushButtonConnection.setEnabled(False)
        self.pushButtonStart.setEnabled(True)
        self.pushButtonStop.setEnabled(False)
    def _on_device_started(self):
        self.pushButtonDisconnect.setEnabled(False)
        self.pushButtonConnection.setEnabled(False)
        self.pushButtonStop.setEnabled(True)
        self.pushButtonStart.setEnabled(False)

    async def _find_device(self) -> BLEDevice | None:
        """ Поиск устройства """
        logger.debug(f"Идёт поиск устройства: {self.schedule_data.device.ble_name}")
        ble_device = await BleakScanner.find_device_by_name(self.schedule_data.device.ble_name, timeout=10)
        if ble_device is None:
            return None
        logger.debug(f"Найдено устройство: {ble_device}")
        return ble_device

    def device_disconnect(self):
        """ Отсоединение от устройства """
        self.device.process_disconnect()

    def device_start_acquisition(self):
        """ Запуск устройства на получение данных """
        self.device.start()

    def _process_device_data(self):
        """ обработка получения данных от inRatDevice (должно быть вынесено в класс Display)"""
        ...

    def device_stop_acquisition(self):
        """ Остановка получения сигнала с inRat """
        self.device.stop()


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
            await self.device_disconnect()

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


 # def set_level_battery(self, usage: InRatUsage):
    #     """ Установка уровня батареи """
    #     battery_capacity = 504 * (10 ** 6)  # мкА * c
    #     # параметры потребления
    #     i_adv, eff_adv, t_adv = 0.02, 1, usage.AdvertisingSeconds
    #     i_con, eff_con, t_con = 15, 0.9, usage.ConnectionSeconds
    #     i_send, eff_send, t_send = 470, 0.7, usage.DataSendSeconds
    #
    #     logger.info(f"\nВ режиме Advertising: {t_adv} с.\n"
    #                 f"В режиме ConnectionSeconds: {t_con} с.\n"
    #                 f"В режиме DataSendSeconds: {t_send} с.\n"
    #                 f"Общее время работы: {t_send + t_adv + t_con} с")
    #
    #     # расчёт потребленной ёмкости в разных режимах
    #     consump_adv = t_adv * i_adv * eff_adv
    #     consump_con = t_con * i_con * eff_con
    #     consump_send = t_send * i_send * eff_send
    #
    #     remain_capacity = battery_capacity - consump_con - consump_send - consump_adv
    #     level = int(remain_capacity / battery_capacity * 100)
    #     self.progressBarLevel.setValue(level)

    # async def _connect_device(self, device: BLEDevice) -> bool:
    #     """ Соединение с устройством """
    #     # соединение
    #     self.device = InRat(ble_device=device)
    #     if await self.device.connect(timeout=10):
    #         logger.debug(f"Выполнено соединение с устройством: {self.device.name}, {self.device.address}")
    #         return True
    #     return False

    # отключение устройства
    # def _device_disconnection(self):
    #     """ Отсоединение от устройства через асинхронную задачу """
    #     logger.debug("Отсоединение от устройства")
    #     if self._loop is None:
    #         self._run_async_loop()
    #
    #     future = asyncio.run_coroutine_threadsafe(
    #         self._disconnect_device(), self._loop
    #     )

    # async def _disconnect_device(self):
    #     """ Отсоединение от устройства """
    #     if not self.device.is_connected:
    #         logger.warning("Устройство уже отключено")
    #         # return
    #
    #     if self.device:
    #         await self.device.disconnect()
    #
    #     # сбросить уровень батареи (когда устр-во отключено)
    #     self.progressBarLevel.setValue(0)
    #     # очистка графика
    #     self.display.clear_plot()
    #     # активация
    #     self.pushButtonConnection.setEnabled(True)
    #     # деактивация
    #     self.pushButtonDisconnect.setEnabled(False)
    #     self.pushButtonStart.setEnabled(False)
    #     self.pushButtonStop.setEnabled(False)
    #     self.comboBoxSampleFreq.setEnabled(False)
    #     self.comboBoxMode.setEnabled(False)
    #     self.device = None

    # запуск устройства
    # def _device_start_acquisition(self):
    #     """ Запуск устройства для получения данных через асинхронную задачу"""
    #     logger.debug("Запущено соединение и запуск устройства")
    #     if self._loop is None:
    #         self._run_async_loop()
    #
    #     self.display.clear_plot()
    #     future = asyncio.run_coroutine_threadsafe(self._start_data_acquisition_impl(), self._loop)

    # async def _start_data_acquisition_impl(self):
    #     """ Запуск устройства для получения данных """
    #     if not self.device.is_connected:    # обрыв соединения (происходит после команды получения данных)
    #         logger.error(f"Устройство {self.device.name} не подключено")
    #         self._device_stop_acquisition()
    #         self._device_disconnection()
    #         return
    #
    #     # активация
    #     self.pushButtonStop.setEnabled(True)
    #     # деактивация
    #     self.comboBoxMode.setEnabled(False)
    #     self.comboBoxSampleFreq.setEnabled(False)
    #     self.pushButtonDisconnect.setEnabled(False)
    #
    #     await self._start_data_acquisition()

    # async def _start_data_acquisition(self):
    #     """ Остановка получения данных"""
    #     if self.device is None or not self.device.is_connected:
    #         logger.debug(f"Устройство {self.schedule_data.device.ble_name} не найдено, либо не подключено")
    #         return
    #
    #     data_queue = asyncio.Queue()
    #     logger.debug(f"{self.schedule_data.device.ble_name} запущен на частоте: {convert_in_rat_sample_rate_to_str(self._settings.DataRateEcg)}")
    #
    #     if await self.device.start_acquisition(data_queue=data_queue, settings=self._settings):
    #         self.is_running = True
    #         # деактивация в режиме получения данных
    #         self.pushButtonStart.setEnabled(False)
    #         # активация
    #         self.pushButtonStop.setEnabled(True)
    #         self.comboBoxSampleFreq.setEnabled(False)
    #         self.pushButtonStartRecording.setEnabled(True)
    #
    #         # установка времени таймеру проверки уровня заряда
    #         self.battery_check_time = time.time()
    #
    #         while self.is_running:
    #             try:
    #                 data = await asyncio.wait_for(data_queue.get(), timeout=1.0)
    #
    #                 if self.start_acquisition_time is None and "start_timestamp" in data:
    #                     self.start_acquisition_time = data["start_timestamp"]
    #
    #                 if "signal" in data and "timestamp" in data and "start_timestamp" in data and "counter" in data:
    #                     start_time = data["start_timestamp"]
    #                     signal = data["signal"]
    #                     time_arr = np.linspace(
    #                         start_time + len(data["signal"]) * (data["counter"] - 1) / self.display.fs,
    #                         start_time + len(data["signal"]) * data["counter"] / self.display.fs, len(signal)) - start_time
    #
    #                     self.display.set_data(time=time_arr, signal=signal)
    #                     self.signal_accept_data.emit(signal)
    #
    #                 if "event" in data:
    #                     if data["event"] == "Temp":
    #                         temp_in_cels = np.round(data["temp"] / 1000, 2)
    #                         self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text=f"{temp_in_cels} °С")
    #                     if data["event"] == "Activity":
    #                         self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text="Activity")
    #                     if data["event"] == "Orientation":
    #                         self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text="Orientation")
    #                     if data["event"] == "Freefall":
    #                         self.display.set_marker(pos=data["timestamp"] - data["start_timestamp"], text="Freefall")
    #
    #                 data_queue.task_done()
    #
    #                 # узнать статус уровня батареи
    #                 if time.time() - self.battery_check_time > 10.0:
    #                     status = await self.device.get_status()
    #                     self.set_level_battery(status.Usage)
    #                     self.battery_check_time = time.time()
    #
    #             except asyncio.TimeoutError:
    #                 continue
    #
    #             except Exception as exp:
    #                 logger.error(f"Ошибка обработки данных с устройства {self.schedule_data.device.ble_name}, {exp}")
    #                 # await self._stop_data_acquisition_impl()
    #                 break
    #
    #     if not self.device.is_connected:  # обрыв соединения (происходит после команды получения данных)
    #         logger.error(f"Потеряно соединение с {self.device.name}!")
    #         self.signal_info_dialog.emit(
    #             f"Потеряно соединение с устройством {self.device.name}!\n"
    #             f"Повторите попытку подключения."
    #         )
    #         self._device_stop_acquisition()
    #         self._device_disconnection()
    #         return

    # остановка устройства
    # def _device_stop_acquisition(self):
    #     """ Остановка устройства через асинхронную задачу """
    #     if self._loop is None:
    #         self._run_async_loop()
    #
    #     future = asyncio.run_coroutine_threadsafe(
    #         self._stop_data_acquisition_impl(),
    #         self._loop
    #     )

    # async def _stop_data_acquisition_impl(self):
    #     """ Остановка получения данных с устройства """
    #     if not self.is_running:
    #         logger.debug(f"Получение данных с {self.schedule_data.device.ble_name} уже остановлено")
    #         return
    #
    #     if await self.device.stop_acquisition():
    #         self.battery_check_time = 0
    #
    #         if self.storage.is_recording:
    #             self.pushButtonStopRecording.click()
    #
    #         self.is_running = False
    #         self.start_acquisition_time = None
    #
    #         # активация при остановке получения данных
    #         self.pushButtonDisconnect.setEnabled(True)
    #         self.pushButtonStart.setEnabled(True)
    #         self.comboBoxMode.setEnabled(True)
    #         self.comboBoxSampleFreq.setEnabled(True)
    #
    #         # деактивация при остановке устройства
    #         self.pushButtonStop.setEnabled(False)
    #         self.pushButtonStartRecording.setEnabled(False)
    #         self.pushButtonStopRecording.setEnabled(False)
    #
    #         logger.info(f"Остановлено получение данных с {self.schedule_data.device.ble_name}")
