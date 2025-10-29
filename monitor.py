from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtCore import Qt

from pyqtgraph import PlotWidget, mkPen
import pyedflib
import numpy as np
from typing import List, Optional
import os

from resources.v1.wdt_monitor import Ui_FormMonitor


class Display(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        font = QFont()
        font.setPointSize(12)

        # label
        self.setLabel("left", "V (мкВ)", pen=mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время (с)", pen=mkPen(color='k'), font=font)

        self.setBackground("w")
        # self.setDisabled(True)

        # Добавляем легенду
        self.addLegend()

    def clear_plot(self):
        """Очистка графика"""
        self.clear()


class SignalMonitor(QDialog, Ui_FormMonitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.NonModal)

        self.display = Display(self)
        self.verticalLayoutMonitor.addWidget(self.display)

        # Цвета для разных сигналов
        self.signal_colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
        self.plots = []  # Ссылки на построенные графики

        # Подключаем кнопки (если они есть в UI)
        if hasattr(self, 'btnClose'):
            self.btnClose.clicked.connect(self.close)

    def load_data(self, path_to_file: str):
        """Загрузка сохраненных данных из EDF файла и отображение на графике"""

        if not os.path.exists(path_to_file):
            self._show_error(f"Файл не найден: {path_to_file}")
            return

        try:
            # Чтение EDF файла
            signals, signal_headers, header = self._read_edf_file(path_to_file)

            # Отображение сигналов
            self._plot_signals(signals, signal_headers, header)

            # Обновление информации о файле
            self._update_file_info(header, signal_headers)

        except Exception as e:
            self._show_error(f"Ошибка загрузки файла: {str(e)}")

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

    def _plot_signals(self, signals: List[np.ndarray],
                      signal_headers: List[dict], header: dict):
        """Отображение сигналов на графике"""
        self.display.clear_plot()
        self.plots.clear()

        # Определяем масштабирование для отображения
        max_signals_to_show = min(6, len(signals))  # Ограничиваем количество сигналов
        vertical_offset = self._calculate_vertical_offset(signals)

        for i, (signal, header_info) in enumerate(zip(signals, signal_headers)):
            if i >= max_signals_to_show:
                break

            # Создаем временную ось
            sample_rate = header_info['sample_rate']
            time_axis = np.arange(len(signal)) / sample_rate

            # Нормализуем и смещаем сигнал для лучшего отображения
            normalized_signal = self._normalize_signal(signal)
            display_signal = normalized_signal + (i * vertical_offset)

            # Выбираем цвет
            color = self.signal_colors[i % len(self.signal_colors)]

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
        if not signals:
            return 100

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
        if not signals:
            return

        # Автоматическое масштабирование
        self.display.enableAutoRange()

        # Устанавливаем подписи осей для первого сигнала
        if signal_headers:
            first_header = signal_headers[0]
            unit = first_header.get('physical_dim', 'мкВ')
            self.display.setLabel("left", f"Амплитуда ({unit})")

        # Добавляем сетку
        self.display.showGrid(x=True, y=True, alpha=0.3)

    def _update_file_info(self, header: dict, signal_headers: List[dict]):
        """Обновление информации о файле в UI"""
        try:
            # Если в UI есть элементы для отображения информации
            if hasattr(self, 'labelPatientName'):
                self.labelPatientName.setText(f"Пациент: {header.get('patient_name', 'N/A')}")

            if hasattr(self, 'labelRecordingDate'):
                date = header.get('recording_date', 'N/A')
                self.labelRecordingDate.setText(f"Дата записи: {date}")

            if hasattr(self, 'labelDuration'):
                duration = header.get('duration', 0)
                self.labelDuration.setText(f"Длительность: {duration:.1f} сек")

            if hasattr(self, 'labelSignalsCount'):
                count = header.get('signals_count', 0)
                self.labelSignalsCount.setText(f"Сигналов: {count}")

            # Обновление информации о каналах
            if hasattr(self, 'listChannels'):
                self.listChannels.clear()
                for i, sh in enumerate(signal_headers):
                    channel_info = (f"{i + 1}. {sh.get('label', 'Unknown')} "
                                    f"({sh.get('sample_rate', 0)} Hz)")
                    self.listChannels.addItem(channel_info)

        except Exception as e:
            print(f"Ошибка обновления информации: {e}")

    def _show_error(self, message: str):
        """Отображение ошибки"""
        print(f"Ошибка: {message}")
        # Можно добавить QMessageBox для показа ошибок пользователю
        from PySide6.QtWidgets import QMessageBox
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