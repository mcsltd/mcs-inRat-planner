import datetime
import os.path
import uuid
import numpy as np
import pyedflib
import wfdb
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from PySide6.QtWidgets import QDialog, QApplication, QMessageBox

from src.resources.record_viewer import Ui_frmRecordViewer
from src.structure import RecordData
from src.resources.wdt_monitor import Ui_FormMonitor


class FormatterTimeAxisItem(pg.AxisItem):
    """ формат mm:ss по оси x """
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

        # self.showGrid(x=True, y=False)
        self.setBackground("w")
        self.setDisabled(True)

    def set_data(self, x: np.ndarray, y: np.ndarray):
        self.plot_signal.setData(x, y)



class RecordViewer(QDialog, Ui_frmRecordViewer):
    """ класс для просмотра сохраненных записей """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)

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

        # signals
        # self.ScrollBarWindow.valueChanged.connect(self._on_scrollbar_moved)
        self.comboBoxSpeed.activated.connect(self._on_speed_changed)


    def load_record(self, record: RecordData):
        """ загрузка записей """
        # проверка существования файлов
        # if (record.file_format == "WFDB" or
        #         not (os.path.exists(f"{record.path}.hea") and os.path.exists(f"{record.path}.dat"))):
        #     QMessageBox.critical(self, "Ошибка загрузки", f"Файл не найден: {record.path}")

        # if record.file_format == "EDF" and not os.path.exists(record.path):
        #     QMessageBox.critical(self, "Ошибка загрузки", f"Файл не найден: {record.path}")

        # чтение сигналов
        signal, header = None, None
        if record.file_format == "WFDB":
            signal, header = self._read_wfdb(file_path=record.path)
        if record.file_format == "EDF":
            self._read_edf(file_path=record.path)
            signal, header = self._read_edf(file_path=record.path)

        # загрузка в буфер
        if signal is not None and header is not None:
            self._buffer_ecg = signal.squeeze()
            self._datetime_start = header["recording_date"]
            self._sample_rate = header["sample_rate"]
            self._duration = header["duration"]
            self._buffer_time = np.arange(0, self._duration, 1 / self._sample_rate)

            # настройка полосы прокрутки
            # self.setup_scrollbar()

            # вывод сигнала в пределах 0 до timebase
            self.idx_start = 0
            self.idx_finish = int(self._timebase * self._sample_rate)

            self.display_ecg.set_data(
                x=self._buffer_time[self.idx_start:self.idx_finish],
                y=self._buffer_ecg[self.idx_start:self.idx_finish]
            )
        _ = 1

    # def setup_scrollbar(self):
    #     """ настройка полосы прокрутки для просмотра сигнала """
    #     self.ScrollBarWindow.setRange(0, self._duration)    # диапазон от 0 до duration
    #     self.ScrollBarWindow.setSingleStep(0.5)   # шаг
    #     self.ScrollBarWindow.setPageStep(10)

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

    def _read_edf(self, file_path: str) -> (list[np.ndarray], dict):
        """ чтение edf файла """
        with pyedflib.EdfReader(file_path) as file:
            # чтение заголовков
            header = {"patient_name": file.getPatientName(), "recording_date": file.getStartdatetime(),
                      "duration": file.getFileDuration(), "signals_count": file.signals_in_file,
                      "sample_rate": file.getSampleFrequency(0)}

            # чтение сигнала
            signals = []
            for i in range(file.signals_in_file):
                signal_data = file.readSignal(i)
                signals.append(signal_data)

        return signals, header

    # def _on_scrollbar_moved(self, value: int):
    #     """ обработка движения полосы прокрутки """
    #     self.idx_start = self._sample_rate * (value * self._timebase)
    #     self.idx_finish = self._sample_rate * ((value + 1) * self._timebase)
    #
    #     # todo: debug
    #     # print(f"{value=} {self.idx_start=} {self.idx_finish=}")
    #
    #     self.display_ecg.set_data(
    #         x=self._buffer_time[self.idx_start:self.idx_finish],
    #         y=self._buffer_ecg[self.idx_start:self.idx_finish]
    #     )

    def _on_speed_changed(self, index=None):
        """ обработка изменения скорости """
        speed = self.comboBoxSpeed.currentData()
        size = self.display_ecg.width()
        self._timebase = int(size / speed)

        self.display_ecg.set_data(x=self._buffer_time[0:self._timebase * self._sample_rate],
                                  y=self._buffer_ecg[0:self._timebase * self._sample_rate])


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