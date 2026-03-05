import queue
import threading
import time

import numpy as np

from pyqtgraph import PlotWidget, PlotDataItem, mkPen

from src.device.device import EcgDataBlock
from src.device.inrat_v1.constants import Pkt


class DisplayScope(PlotWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.timebase = 10 # in seconds
        self.buffer_ecg = np.zeros(Pkt.SamplesCountEcg)

        self.plot_ecg: PlotDataItem = self.plot()
        self.ecg = EcgDataBlock()

        self._running = False
        self._work = None
        self._input_queue = queue.Queue()

        self.setLabel("left", "V")
        self.setLabel("bottom", "t (с)")

        self.set_display()

    def start(self):
        """ запуск обработки очереди """
        while not self._input_queue.empty():
            self._input_queue.get_nowait()

        if not self._running:
            self._running = True
            self._work = threading.Thread(target=self._worker_thread)
            self._work.start()

    def process_input(self, datablock: EcgDataBlock):
        """ обработка входящего блока данных """
        self.ecg = datablock
        self.set_display()

    def set_display(self):
        """ отображение ЭКГ на графике """
        self.buffer_ecg = self.ecg.ecg_channels
        self.plot_ecg.setData(self.buffer_ecg)

    def process_output(self):
        """ обработка остановки """
        return None

    def process_stop(self):
        """ обработка остановки """
        self.clear()
        self.plot_ecg: PlotDataItem = self.plot()   # Todo: плохое решение


    def _transmit_data(self, data):
        """ получение данных от класса inrat"""
        self._input_queue.put(data, False)

    def _worker_thread(self):
        """ запуск цикла на обработку и получение данных """
        while self._running:
            try:
                data = self._input_queue.get(block=False)
                self.process_input(data)
            except:
                pass

            try:
                data = self.process_output()
            except:
                pass

            time.sleep(0.001)

    def stop(self):
        """ остановка """
        print("Display остановлен")
        self._running = False
        if self._work:
            self._work.join(1.0)
            self._work = None
        self.process_stop()


