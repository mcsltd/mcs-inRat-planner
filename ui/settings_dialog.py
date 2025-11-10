from PySide6.QtCore import QModelIndex, QObject, Signal
from PySide6.QtGui import QFont, Qt, QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QHBoxLayout, QGroupBox, QSpinBox, QLabel, \
    QSpacerItem, QSizePolicy, QPushButton, QMessageBox

from db.database import connection
from db.models import Schedule
from resources.v1.frm_localConfig import Ui_FrmMainConfig
from ui.helper_dialog import DialogHelper

PATH_TO_ICON = "resources/v1/icon_app.svg"

class ConfigSignals(QObject):
    """ Сигналы настроек """
    max_devices_changed = Signal(int)
    archive_restored = Signal()
    archive_deleted = Signal()
    data_changed = Signal()


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

        self.verticalLayout.addWidget(self.label)
        # self.verticalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.horizontalLayoutControlTable)
        self.setLayout(self.verticalLayout)

    @classmethod
    def convert_seconds_to_str(cls, seconds) -> str | None:
        if seconds / 3600 >= 1:
            return f"{seconds // 3600} ч."
        if seconds / 60 >= 1:
            return f"{seconds // 60} мин."
        return f"{seconds} с."


class DlgMainConfig(QDialog, Ui_FrmMainConfig):
    """ Главное окно настроек """

    def __init__(self, cnt_device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))
        self.signals = ConfigSignals()

        self._idx_selected_widget = 0
        self.widgets = [
            WidgetCfgGeneral(self, cnt_device),
        ]
        self.set_widgets()

        self.listWidget.clicked.connect(self.setup_widget)
        self.pushButtonCancel.clicked.connect(self.close)

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


class WidgetCfgGeneral(WidgetCfg):
    """Виджет настроек конфигурации BLE устройств"""

    def __init__(self, parent=None, cnt_device=2, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.parent_dialog: DlgMainConfig = parent

        self.name = "Общее"
        self.setup_ui()
        self.setup_ble_settings(cnt_device)
        self.archive_recovery_ui()
        self.archive_remove_ui()
        self.verticalLayout.addStretch()  # Растягивающийся spacer

    def setup_ble_settings(self, cnt_device: int):
        """Настройка интерфейса для BLE настроек"""
        self.ble_connection_group = QGroupBox("Настройки подключения устройств")
        ble_connection_layout = QVBoxLayout(self.ble_connection_group)
        connection_limit_layout = QHBoxLayout()
        self.label_cnt_device = QLabel("Максимальное количество подключаемых устройств:")
        connection_limit_layout.addWidget(self.label_cnt_device)
        self.connection_spinbox = QSpinBox()
        self.connection_spinbox.setRange(1, 4)
        self.connection_spinbox.setValue(cnt_device)
        self.connection_spinbox.setSuffix(" устройств")
        self.connection_spinbox.setFixedWidth(120)
        connection_limit_layout.addWidget(self.connection_spinbox)
        connection_limit_layout.addStretch()
        ble_connection_layout.addLayout(connection_limit_layout)
        self.v_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # Поясняющая надпись
        info_label = QLabel("• Увеличение количества может повлиять на стабильность работы")
        info_label.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")
        ble_connection_layout.addWidget(info_label)

        self.connection_spinbox.valueChanged.connect(self.on_max_devices_changed)
        self.verticalLayout.addWidget(self.ble_connection_group)

    def on_max_devices_changed(self, value: int):
        """ Обработчик изменения максимального количества устройств """
        if self.parent_dialog and hasattr(self.parent_dialog, "signals"):
            self.parent_dialog.signals.max_devices_changed.emit(value)

    def archive_recovery_ui(self):
        """ Интерфейс восстановления архивированных данных """
        self.restore_group = QGroupBox("Восстановление архивных расписаний и записей")
        restore_layout = QVBoxLayout(self.restore_group)

        self.label_archive_info = QLabel(f"Всего архивированных расписаний: 0")
        self.set_label_count_archived_schedule()

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.label_archive_info)
        info_layout.addStretch()
        restore_layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        self.btn_restore_all = QPushButton("Восстановить всё")
        self.btn_restore_all.clicked.connect(self.on_restore_all)

        button_layout.addWidget(self.btn_restore_all)
        button_layout.addStretch()
        restore_layout.addLayout(button_layout)

        # Добавляем группы в основной layout
        self.verticalLayout.addWidget(self.restore_group)

    @connection
    def set_label_count_archived_schedule(self, session):
        cnt_del_schedule = Schedule.get_deleted_count(session)
        self.label_archive_info.setText(f"Всего архивированных расписаний: {cnt_del_schedule}")

    def on_restore_all(self):
        """ Обработчик восстановления всех архивных расписаний, устройств, записей, объектов """
        if self.parent_dialog and hasattr(self.parent_dialog, "signals"):
            self.parent_dialog.signals.archive_restored.emit()
            self.parent_dialog.signals.data_changed.emit()

    def archive_remove_ui(self):
        """ Интерфейс удаления архивированных данных """
        # Группа удаления данных
        self.delete_group = QGroupBox("Удаление архивных расписаний и записей")
        delete_layout = QVBoxLayout(self.delete_group)

        button_layout = QHBoxLayout()
        self.btn_delete = QPushButton("Удалить всё")

        self.btn_delete.clicked.connect(self.on_delete_all)

        button_layout.addWidget(self.btn_delete)
        button_layout.addStretch()
        delete_layout.addLayout(button_layout)

        # Добавляем группы в основной layout
        self.verticalLayout.addWidget(self.delete_group)

    def on_delete_all(self):
        """ Обработчик удаления всех архивных расписаний, устройств, записей, объектов """

        res = DialogHelper.show_confirmation_dialog(
            parent=self,
            title="Удаление архивных данных",
            message="Вы уверены что хотите удалить архивные данные?\nУдаленные данные нельзя будет восстановить.",
            icon=QMessageBox.Icon.Warning
        )

        if res:
            if self.parent_dialog and hasattr(self.parent_dialog, "signals"):
                self.parent_dialog.signals.archive_deleted.emit()
                self.parent_dialog.signals.data_changed.emit()

"""class WidgetCfgDevice(WidgetCfg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Устройства"
        self.setup_ui()
        self.set_data_table()
        self.setup_ble_settings()

    @connection
    def set_data_table(self, session):
        columns = ["№", "Название"]
        data = []
        devices = Device.fetch_all(session)
        for idx, d in enumerate(devices):
            d = d.to_dataclass()
            data.append([idx + 1, d.ble_name])


    def setup_ble_settings(self):
        # Группа настроек подключения BLE
        self.ble_connection_group = QGroupBox("Настройки подключения BLE устройств")
        ble_connection_layout = QVBoxLayout(self.ble_connection_group)

        # Настройка максимального количества подключений
        connection_limit_layout = QHBoxLayout()
        self.label_cnt_device = QLabel("Максимальное количество подключаемых устройств:")
        connection_limit_layout.addWidget(self.label_cnt_device)

        self.connection_spinbox = QSpinBox()
        self.connection_spinbox.setRange(1, 4)
        self.connection_spinbox.setValue(2)
        self.connection_spinbox.setSuffix(" устройств")
        self.connection_spinbox.setFixedWidth(120)
        connection_limit_layout.addWidget(self.connection_spinbox)

        self.v_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        connection_limit_layout.addStretch()
        ble_connection_layout.addLayout(connection_limit_layout)

        # Поясняющая надпись
        info_label = QLabel("• Увеличение количества может повлиять на стабильность работы")
        info_label.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")
        ble_connection_layout.addWidget(info_label)

        self.verticalLayout.insertWidget(1, self.ble_connection_group)
        self.verticalLayout.insertItem(2, self.v_spacer)"""
"""class WidgetCfgSchedule(WidgetCfg):
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
        # self.table.setData(data=data, description=columns)"""
"""
class WidgetCfgObject(WidgetCfg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Объекты"
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
        # self.table.setData(data=data, description=columns)
"""
"""
class WidgetCfgExperiment(WidgetCfg):
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
        # self.table.setData(data=data, description=columns)
"""

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QLabel, QWidget, QDialog

    app = QApplication([])
    window = DlgMainConfig()
    window.show()
    app.exec()