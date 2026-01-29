import wfdb
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from structure import RecordData, ScheduleData

from config import PATH_TO_ICON


from pyqtgraph import PlotWidget, mkPen
import pyedflib
import numpy as np
from typing import List
import os

from resources.v1.wdt_monitor import Ui_FormMonitor


class Display(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pen = mkPen("k")
        font = QFont("Arial", 11)

        self.setLabel("left", "V (мкВ)", pen=mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время (с)", pen=mkPen(color='k'), font=font)
        for ax in ["bottom", "left"]:
            self.getAxis(ax).label.setFont(font)
            self.getAxis(ax).setPen(pen)
            self.getAxis(ax).setTextPen(pen)
            self.getAxis(ax).setTickPen(pen)
            self.getAxis(ax).setTickFont(font)

        self.setBackground("w")
        # self.setDisabled(True)

        # Добавляем легенду
        self.addLegend()

    def clear_plot(self):
        """Очистка графика"""
        self.clear()


class SignalMonitor(QDialog, Ui_FormMonitor):

    def __init__(self, schedule_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowIcon(QIcon(PATH_TO_ICON))

        title=f"Сигнал ЭКГ с объекта \"{schedule_data.object.name}\""
        self.setWindowTitle(title)

        self.display = Display(self)
        self.verticalLayoutMonitor.addWidget(self.display)

        # Цвета для разных сигналов
        self.signal_colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
        self.plots = []  # Ссылки на построенные графики

        self.schedule_data: ScheduleData = schedule_data
        self.record_data: RecordData | None = None


    def load_record(self, record_data: RecordData):
        """Загрузка сохраненных данных из EDF файла и отображение на графике"""

        if record_data.file_format == "WFDB":
            if not os.path.exists(f"{record_data.path}.hea") or not os.path.exists(f"{record_data.path}.dat"):
                self._show_error(f"Файл не найден: {record_data.path}")
                self.accept()
                return

        if record_data.file_format == "EDF" and not os.path.exists(record_data.path):
            self._show_error(f"Файл не найден: {record_data.path}")
            self.accept()
            return

        self.record_data = record_data

        try:
            # загрузка информации о записи
            self._load_info()

            if record_data.file_format == "WFDB":
                # Чтение WFDB файла
                signals, signal_headers, header = self._read_wfdb_file(record_data.path)

                # Отображение сигналов
                self._plot_signals(signals, signal_headers, header)

            elif record_data.file_format == "EDF":
                # Чтение EDF файла
                signals, signal_headers, header = self._read_edf_file(record_data.path)

                # Отображение сигналов
                self._plot_signals(signals, signal_headers, header)

            else:
                raise ValueError("Не поддерживаемый формат файла!")

            # Обновление информации о файле
            # self._update_file_info(header, signal_headers)

        except Exception as e:
            self._show_error(f"Ошибка загрузки файла: {str(e)}")

    def _load_info(self):
        """ Отображение информации о записи """
        self.labelExperimentValue.setText(self.schedule_data.experiment.name)
        self.labelDeviceValue.setText(self.schedule_data.device.ble_name)
        self.labelObjectValue.setText(self.schedule_data.object.name)
        self.labelFormatValue.setText(self.record_data.file_format)
        self.labelDurationValue.setText(f"{self.record_data.sec_duration} с.")
        self.labelSamplingRateValue.setText(f"{self.record_data.sampling_rate} Гц")
        self.labelStartTimeValue.setText(f"{str(self.record_data.datetime_start.replace(microsecond=0))}")

    def _read_edf_file(self, file_path: str):
        """Чтение данных из EDF файла"""
        with pyedflib.EdfReader(file_path) as file:
            # Получаем заголовок файла
            header = {
                'patient_name': file.getPatientName(),
                'recording_date': file.getStartdatetime(),
                'duration': file.getFileDuration(),
                'signals_count': file.signals_in_file
            }

            # Получаем информацию о сигналах
            signal_headers = []
            for i in range(file.signals_in_file):
                signal_headers.append({
                    'label': file.getLabel(i),
                    'sample_rate': file.getSampleFrequency(i),
                    'physical_dim': file.getPhysicalDimension(i),
                    'samples_count': file.getNSamples()[i]
                })

            # Читаем данные сигналов
            signals = []
            for i in range(file.signals_in_file):
                signal_data = file.readSignal(i)
                signals.append(signal_data)

        return signals, signal_headers, header

    def _read_wfdb_file(self, file_path: str):
        """Чтение данных из WFDB файла"""
        try:
            # Убираем расширение .dat или .hea если есть
            base_path = file_path
            if file_path.endswith('.dat') or file_path.endswith('.hea'):
                base_path = file_path[:-4]
            # Читаем запись с помощью wfdb
            record = wfdb.rdrecord(base_path)

            # Получаем сигналы (уже в виде numpy array)
            signals = record.p_signal.T if record.p_signal is not None else record.d_signal.T

            # Если сигнал одноканальный, преобразуем в 2D массив для единообразия
            if signals.ndim == 1:
                signals = signals.reshape(1, -1)

            # Создаем заголовок файла
            header = {
                'patient_name': getattr(record, 'patient_name', 'Неизвестно'),
                'recording_date': getattr(record, 'base_date', 'Неизвестно'),
                'duration': record.sig_len / record.fs if record.fs > 0 else 0,
                'signals_count': record.n_sig,
                'sample_rate': record.fs
            }

            # Создаем информацию о сигналах
            signal_headers = []
            for i in range(record.n_sig):
                signal_headers.append({
                    'label': record.sig_name[i] if i < len(record.sig_name) else f'Channel_{i + 1}',
                    'sample_rate': record.fs,
                    'physical_dim': record.units[i] if i < len(record.units) else 'uV',
                    'samples_count': record.sig_len,
                    'gain': record.adc_gain[i] if i < len(record.adc_gain) else 1,
                    'baseline': record.baseline[i] if i < len(record.baseline) else 0
                })

            return signals, signal_headers, header

        except Exception as e:
            raise Exception(f"Ошибка чтения WFDB файла: {str(e)}")

    def _plot_signals(self, signals: List[np.ndarray],
                      signal_headers: List[dict], header: dict):
        """Отображение сигналов на графике"""
        self.display.clear_plot()
        self.plots.clear()

        # Определяем масштабирование для отображения
        vertical_offset = self._calculate_vertical_offset(signals)

        for signal, header_info in zip(signals, signal_headers):

            # Создаем временную ось
            sample_rate = header_info['sample_rate']
            time_axis = np.arange(len(signal)) / sample_rate

            # Нормализуем и смещаем сигнал для лучшего отображения
            normalized_signal = self._normalize_signal(signal)
            display_signal = normalized_signal

            # Выбираем цвет
            color = self.signal_colors[0]

            # Строим график
            plot = self.display.plot(
                time_axis,
                display_signal,
                pen=mkPen(color=color, width=1),
                name=header_info['label']
            )
            self.plots.append(plot)

        # Настраиваем отображение графика
        self._configure_plot_display(signals, signal_headers, vertical_offset)

    def _calculate_vertical_offset(self, signals: List[np.ndarray]) -> float:
        """Вычисление вертикального смещения между сигналами"""

        # Используем стандартное отклонение для определения смещения
        all_std = np.std(np.concatenate([sig - np.mean(sig) for sig in signals]))
        return max(50, all_std * 4)

    def _normalize_signal(self, signal: np.ndarray) -> np.ndarray:
        """Нормализация сигнала для отображения"""
        if len(signal) == 0:
            return signal

        # Убираем постоянную составляющую и нормализуем
        signal_clean = signal - np.mean(signal)
        signal_std = np.std(signal_clean)

        if signal_std > 0:
            return signal_clean / signal_std
        else:
            return signal_clean

    def _configure_plot_display(self, signals: List[np.ndarray],
                                signal_headers: List[dict], vertical_offset: float):
        """Настройка отображения графика"""


        # Автоматическое масштабирование
        self.display.enableAutoRange()

        # Устанавливаем подписи осей для первого сигнала
        if signal_headers:
            first_header = signal_headers[0]
            unit = first_header.get('physical_dim', 'мкВ')
            self.display.setLabel("left", f"Амплитуда ({unit})")

        # Добавляем сетку
        self.display.showGrid(x=True, y=True, alpha=0.3)

    def _show_error(self, message: str):
        """Отображение ошибки"""
        QMessageBox.critical(self, "Ошибка загрузки", message)

    def clear_display(self):
        """Очистка графика и сброс состояния"""
        self.display.clear_plot()
        self.plots.clear()

        # Сброс информации о файле
        if hasattr(self, 'labelPatientName'):
            self.labelPatientName.setText("Пациент: ")
        if hasattr(self, 'labelRecordingDate'):
            self.labelRecordingDate.setText("Дата записи: ")
        if hasattr(self, 'labelDuration'):
            self.labelDuration.setText("Длительность: ")
        if hasattr(self, 'labelSignalsCount'):
            self.labelSignalsCount.setText("Сигналов: ")
        if hasattr(self, 'listChannels'):
            self.listChannels.clear()

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.clear_display()
        event.accept()


if __name__ == "__main__":

    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    window = SignalMonitor()
    window.show()
    app.exec()