from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QHBoxLayout

from db.database import connection
from db.models import Device, Experiment, Schedule, Object
from resources.v1.frm_localConfig import Ui_FrmMainConfig
from tools.modview import GenericTableWidget


class DlgMainConfig(QDialog, Ui_FrmMainConfig):
    """ Главное окно настроек """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._idx_selected_widget = 0
        self.widgets = [WidgetCfgGeneral(), WidgetCfgDevice(), WidgetCfgExperiment(), WidgetCfgObject()]
        self.set_widgets()

        self.listWidget.clicked.connect(self.setup_widget)

    def setup_widget(self, index: QModelIndex):
        model_idx = self.listWidget.selectedIndexes()[0]
        idx = model_idx.row()
        if idx != self._idx_selected_widget:
            # удаление старого виджета
            crt_widget = self.widgets[self._idx_selected_widget]
            self.horizontalLayoutMainConfig.removeWidget(crt_widget)
            crt_widget.hide()

            # добавление нового виджета
            self._idx_selected_widget = idx
            new_widget = self.widgets[self._idx_selected_widget]
            self.horizontalLayoutMainConfig.addWidget(self.widgets[self._idx_selected_widget])
            new_widget.show()

    def set_widgets(self):
        for idx, widget in enumerate(self.widgets):
            self.listWidget.addItem(widget.name)
            if self._idx_selected_widget == idx:
                self.horizontalLayoutMainConfig.addWidget(widget)


class WidgetCfg(QWidget):
    """ Базовый класс виджета настроек """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = None

    def setup_ui(self):
        self.font = QFont("Arial", 11, QFont.Bold)
        self.verticalLayout = QVBoxLayout()
        self.horizontalLayoutControlTable = QHBoxLayout()

        self.label = QLabel(self.name, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.label.setFont(self.font)

        self.table = GenericTableWidget()
        self.btnAdd = QPushButton("Добавить")
        self.horizontalLayoutControlTable.addWidget(self.btnAdd)
        self.btnUpdate = QPushButton("Изменить")
        self.horizontalLayoutControlTable.addWidget(self.btnUpdate)
        self.btnDelete = QPushButton("Удалить")
        self.horizontalLayoutControlTable.addWidget(self.btnDelete)

        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.horizontalLayoutControlTable)
        self.setLayout(self.verticalLayout)

    @classmethod
    def convert_seconds_to_str(cls, seconds) -> str | None:
        if seconds / 3600 >= 1:
            return f"{seconds // 3600} ч."
        if seconds / 60 >= 1:
            return f"{seconds // 60} мин."
        return f"{seconds} с."


class WidgetCfgGeneral(WidgetCfg):
    """ Класс для общих настроек приложения """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Общее"
        self.setup_ui()
        self.delete_table()

    def delete_table(self):
        self.verticalLayout.removeWidget(self.table)

        for w in [self.btnUpdate, self.btnAdd, self.btnDelete]:
            self.horizontalLayoutControlTable.removeWidget(w)
            w.hide()

        self.table.hide()

class WidgetCfgDevice(WidgetCfg):
    """ Класс для настройки устройств """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Устройства"
        self.setup_ui()
        self.set_data_table()

    @connection
    def set_data_table(self, session):
        columns = ["№", "Название"]
        data = []
        devices = Device.fetch_all(session)
        for idx, d in enumerate(devices):
            d = d.to_dataclass()
            data.append([idx + 1, d.ble_name])

        self.table.setData(data=data, description=columns)

class WidgetCfgExperiment(WidgetCfg):
    """ Класс для настройки экспериментов """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Эксперименты"
        self.setup_ui()
        self.set_data_table()

    @connection
    def set_data_table(self, session):
        data = []
        columns = ["№", "Название"]
        experiments = Experiment.fetch_all(session)
        for idx, exp in enumerate(experiments):
            exp = exp.to_dataclass()
            data.append([idx + 1, exp.name])
        self.table.setData(data=data, description=columns)

class WidgetCfgSchedule(WidgetCfg):
    """ Класс для настройки расписаний """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Расписания"
        self.setup_ui()
        self.set_data_table()

    @connection
    def set_data_table(self, session):
        data = []
        columns = ["№", "Эксперимент", "Дата начала", "Дата окончания", "Длительность\nзаписи", "Периодичность\nзаписи"]
        schedules = Schedule.fetch_all(session)
        for idx, sch in enumerate(schedules):
            sch = sch.to_dataclass(session)
            data.append([idx + 1,
                         sch.experiment.name,
                         sch.datetime_start,
                         sch.datetime_finish,
                         self.convert_seconds_to_str(sch.sec_interval),
                         self.convert_seconds_to_str(sch.sec_duration)]
            )
        self.table.setData(data=data, description=columns)

class WidgetCfgObject(WidgetCfg):
    """ Класс для настройки объектов исследования """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Объекты исследования"
        self.setup_ui()
        self.set_data_table()

    @connection
    def set_data_table(self, session):
        data = []
        columns = ["№", "Название"]
        objs = Object.fetch_all(session)
        for idx, obj in enumerate(objs):
            obj = obj.to_dataclass()
            data.append([idx + 1, obj.name])
        self.table.setData(data=data, description=columns)



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QLabel, QWidget, QDialog

    app = QApplication([])
    window = DlgMainConfig()
    window.show()
    app.exec()