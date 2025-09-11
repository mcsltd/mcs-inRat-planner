from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import QDialog

from ui.v1.dlg_input_schedule import Ui_DlgCreateNewSchedule



class DlgCreateSchedule(Ui_DlgCreateNewSchedule, QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # setup QDateTimeEdit
        self.dateTimeEditStartRecord.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.dateTimeEditStartRecord.setCalendarPopup(True)

        # set default value for ComboBox
        self.comboBoxFreq.setCurrentIndex(1)            # default 1000 Hz
        self.comboBoxIntervalDim.setCurrentIndex(1)

        # set default value for QLineEdit
        self.spinBoxDuration.setValue(30)
        self.spinBoxInterval.setValue(1)
