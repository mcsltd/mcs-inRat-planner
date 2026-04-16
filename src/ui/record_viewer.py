import datetime
import os.path
import uuid
import numpy as np
import pyedflib
import wfdb
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from PySide6.QtWidgets import QDialog, QApplication, QMessageBox, QMenuBar

from src.resources.record_viewer import Ui_frmRecordViewer
from src.structure import RecordData, ScheduleData
from src.resources.wdt_monitor import Ui_FormMonitor


class FormatterTimeAxisItem(pg.AxisItem):
    """ формат mm:ss по оси x """
    # todo: разобраться с ошибкой обозначения интервала внутри секунд
    def tickStrings(self, values, scale, spacing) -> list[str]:
        strings = []
        for value in values:
            minutes = int(value // 60)
            seconds = int(value % 60)
            strings.append(f"{minutes:02d}:{seconds:02d}")
        return strings

class DisplaySignal(pg.PlotWidget):
    """ класс для отображения сигналов """
    def __init__(self, *args, **kwargs):
        kwargs['axisItems'] = {'bottom': FormatterTimeAxisItem(orientation="bottom")}
        super().__init__(*args, **kwargs)

        self._scale = None
        self._timebase = None

        # настройка подписей к графику
        pen = pg.mkPen("k")
        font = QFont("Arial", 11)
        self.setLabel("left", "ЭКГ", units="V", pen=pg.mkPen(color='k'), font=font)
        self.setLabel("bottom", "Время", pen=pg.mkPen(color='k'), font=font)
        for ax in ["bottom", "left"]:
            self.getAxis(ax).label.setFont(font)
            self.getAxis(ax).setPen(pen)
            self.getAxis(ax).setTextPen(pen)
            self.getAxis(ax).setTickFont(font)

        self.plot_signal = self.plot(pen=pg.mkPen(color="r", width=1))

        self.setEnabled(False)
        # self.showGrid(x=True, y=False)
        self.setBackground("w")

    def set_data(self, x: np.ndarray, y: np.ndarray):
        self.plot_signal.setData(x, y)
        self.setXRange(x[0], x[-1], padding=0)

    def set_timebase(self, value):
        self._timebase = value


class RecordViewer(QDialog, Ui_frmRecordViewer):
    """ класс для просмотра сохраненных записей """

    def __init__(self, schedule: ScheduleData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)

        self.schedule: ScheduleData = schedule

        self.current_position = 0
        self._buffer_ecg = np.array([])
        self._buffer_time = np.array([])
        self._datetime_start: None | datetime.datetime = None
        self._sample_rate = None
        self._duration = None

        self.display_ecg = DisplaySignal()
        self.verticalLayoutMonitor.insertWidget(1, self.display_ecg)

        # для настроек отображения сигнала
        self.idx_start = 0
        self.idx_finish = 0
        self._timebase = self.display_ecg.width() / 12.5  # in seconds

        # настройка выпадающих списков
        speed = [("12.5 мм/c", 12.5), ("25 мм/c", 25.5), ("50 мм/c", 50), ("100 мм/c", 100)]
        for v, d in speed:
            self.comboBoxSpeed.addItem(v, userData=d)
        self.comboBoxSpeed.setCurrentIndex(0)

        sens = [("5 мм/мВ", 5*1e-3), ("10 мм/мВ", 10*1e-3), ("20 мм/мВ", 20*1e-3), ("40 мм/мВ", 40*1e-3),]
        for v, d in sens:
            self.comboBoxGain.addItem(v, userData=d)
        self.comboBoxGain.setCurrentIndex(1)

        # signals
        self.comboBoxSpeed.activated.connect(self._on_speed_changed)
        self.comboBoxGain.activated.connect(self._on_gain_changed)
        self.horizontalSlider.valueChanged.connect(self._on_slider_changed)

    def load_record(self, record: RecordData) -> bool:
        """ загрузка записей """
        # todo добавить проверку заголовков файла

        if (record.file_format == "WFDB" and
                not (os.path.exists(f"{record.path}.hea") and os.path.exists(f"{record.path}.dat"))):
            QMessageBox.critical(self, "Ошибка загрузки", f"Файл не найден: {record.path}")
            return False

        if record.file_format == "EDF" and not os.path.exists(record.path):
            QMessageBox.critical(self, "Ошибка загрузки", f"Файл не найден: {record.path}")
            return False

        # чтение сигналов
        signal, header = None, None
        if record.file_format == "WFDB":
            signal, header = self._read_wfdb(file_path=record.path)
        if record.file_format == "EDF":
            self._read_edf(file_path=record.path)
            signal, header = self._read_edf(file_path=record.path)

        if signal is None or header is None:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить данные из файла: {record.path}")

        # загрузка в буфер
        self._buffer_ecg = self._normalize_signal(signal.squeeze()) / 1e3
        self._datetime_start = header["recording_date"]
        self._sample_rate = header["sample_rate"]
        self._duration = header["duration"]
        self._buffer_time = np.arange(0, self._duration, 1 / self._sample_rate)

        # настройка полосы прокрутки
        self.setup_slider()

        # вывод сигнала в пределах 0 до timebase
        idx_start = 0
        idx_finish = int(self._timebase * self._sample_rate)
        self.display_ecg.set_data(x=self._buffer_time[idx_start:idx_finish], y=self._buffer_ecg[idx_start:idx_finish])

        self.set_title_to_record_info()
        return True

    def set_title_to_record_info(self):
        """ обновление заголовка с информацией о записи """
        text_dur = None
        if self._duration:
            m = int(self._duration // 60)
            m_text = f"{m} мин. " if m != 0 else ""
            text_dur = m_text + f"{int(self._duration % 60)} c."

        sr = None
        if self._sample_rate:
            sr = int(self._sample_rate)
        text = f"Запись c объекта \"{self.schedule.object.name}\" в эксперименте \"{self.schedule.experiment.name}\", длительность: {text_dur}, частота: {sr} Гц"
        self.setWindowTitle(text)

    def _read_edf(self, file_path: str) -> (list[np.ndarray], dict):
        """ чтение edf файла """
        with pyedflib.EdfReader(file_path) as file:
            # чтение заголовков
            header = {"patient_name": file.getPatientName(), "recording_date": file.getStartdatetime(),
                      "duration": file.getFileDuration(), "signals_count": file.signals_in_file,
                      "sample_rate": file.getSampleFrequency(0)}
            # чтение сигнала
            signal_data = file.readSignal(0)
        return signal_data, header

    def _read_wfdb(self, file_path: str):
        """ чтение wfdb файла """
        if file_path.endswith('.dat') or file_path.endswith('.hea'):
            file_path = file_path[:-4]

        record = wfdb.rdrecord(file_path)
        signals = record.p_signal.T if record.p_signal is not None else record.d_signal.T
        if signals.ndim == 1:
            signals = signals.reshape(1, -1)

        header = {
            'patient_name': getattr(record, 'patient_name', 'Неизвестно'),
            'recording_date': getattr(record, 'base_datetime', 'Неизвестно'),
            'duration': record.sig_len / record.fs if record.fs > 0 else 0,
            'signals_count': record.n_sig,
            'sample_rate': record.fs
        }
        return signals, header

    def _on_slider_changed(self, value: int):
        """ обработка движения полосы прокрутки """
        self.current_position = value
        self.update_display()

    def setup_slider(self):
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(self._duration)
        self.horizontalSlider.setPageStep(10)

    def _normalize_signal(self, signal: np.ndarray) -> np.ndarray:
        """ нормализация сигнала для отображения """
        if len(signal) == 0:
            return signal
        signal_clean = signal - np.mean(signal)
        signal_std = np.std(signal_clean)
        if signal_std > 0:
            return signal_clean / signal_std
        else:
            return signal_clean

    def _on_speed_changed(self, index=None):
        """ обработка изменения скорости """
        speed = self.comboBoxSpeed.currentData()

        # расчёт масштаба времени
        pixels_per_mm = QApplication.primaryScreen().physicalDotsPerInch() / 25.4
        width_mm = self.display_ecg.width() / pixels_per_mm
        self._timebase = int(width_mm / speed)

        # обновление графика
        self.update_display()

    def _on_gain_changed(self, index=None):
        """ обработка изменения амплитуды """
        sens = self.comboBoxGain.currentData()
        pixels_per_mm = QApplication.primaryScreen().physicalDotsPerInch() / 25.4
        height_mm = self.display_ecg.height() / pixels_per_mm
        scale = sens / height_mm
        self.update_display()

    def update_display(self):
        """ обновить отображение сигнала в окне """
        idx_start = int(self._sample_rate * self.current_position)
        idx_finish = int(self._sample_rate * (self.current_position + self._timebase))

        if self.current_position + self._timebase >= self._duration:
            idx_start = int((self._duration - self._timebase) * self._sample_rate)
            idx_finish = int(self._duration * self._sample_rate)

        visible_time_array = self._buffer_time[idx_start:idx_finish]
        visible_signal = self._buffer_ecg[idx_start:idx_finish]

        self.display_ecg.set_data(x=visible_time_array, y=visible_signal)

    def resizeEvent(self, arg__1, /):
        self._on_speed_changed()


if __name__ == "__main__":
    app = QApplication()

    record_data_wfdb = RecordData(
        sec_duration=1200,
        file_format="WFDB",
        datetime_start=datetime.datetime.now(),
        schedule_id=uuid.uuid4(),
        sampling_rate=2000,
        status="Ok",
        path=r"C:\Users\andmo\.inRat planner\data\inRat-1-1024\\\test_1024_2026-4-7_11-10-12",
    )

    record_data_edf = RecordData(
        sec_duration=4,
        file_format="EDF",
        datetime_start=datetime.datetime.now(),
        schedule_id=uuid.uuid4(),
        sampling_rate=500,
        status="Ok",
        path=r"C:\Users\andmo\.inRat planner\data\inRat-1-1064\test_1064_2026-4-9_13-55-26.edf",
    )

    dlg = RecordViewer()
    dlg.load_record(record=record_data_wfdb)
    dlg.show()

    app.exec()