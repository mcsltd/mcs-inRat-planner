import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateTimeEdit, QCalendarWidget, QDialogButtonBox, QGridLayout
)
from PySide6.QtCore import Qt, QDateTime


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание расписания записи ЭКГ")
        self.setMinimumWidth(500)

        # Создаем макет
        main_layout = QVBoxLayout(self)

        # --- Группа: Информация о пациенте и устройстве ---
        info_group = QGroupBox("Информация")
        info_layout = QGridLayout(info_group)

        # Поле 1: Имя пациента
        info_layout.addWidget(QLabel("Имя пациента:"), 0, 0)
        self.patient_name_edit = QLineEdit()
        info_layout.addWidget(self.patient_name_edit, 0, 1)

        # Поле 2: Серийный номер устройства
        info_layout.addWidget(QLabel("Серийный номер:"), 1, 0)
        self.device_sn_edit = QLineEdit()
        info_layout.addWidget(self.device_sn_edit, 1, 1)

        main_layout.addWidget(info_group)

        # --- Группа: Параметры записи ---
        record_group = QGroupBox("Параметры записи")
        record_layout = QGridLayout(record_group)

        # Поле 3: Длительность записи (в секундах)
        record_layout.addWidget(QLabel("Длительность (сек):"), 0, 0)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 3600)  # от 1 секунды до 1 часа
        self.duration_spin.setSuffix(" сек")
        self.duration_spin.setValue(30)  # значение по умолчанию
        record_layout.addWidget(self.duration_spin, 0, 1)

        # Поле 5: Частота дискретизации (Гц)
        record_layout.addWidget(QLabel("Частота (Гц):"), 1, 0)
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(100, 2000)  # примерный диапазон для ЭКГ
        self.sample_rate_spin.setSuffix(" Гц")
        self.sample_rate_spin.setValue(500)  # значение по умолчанию
        record_layout.addWidget(self.sample_rate_spin, 1, 1)

        # Поле 6: Формат записи
        record_layout.addWidget(QLabel("Формат:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "WFDB", "TXT"])
        record_layout.addWidget(self.format_combo, 2, 1)

        main_layout.addWidget(record_group)

        # --- Группа: Расписание ---
        schedule_group = QGroupBox("Расписание")
        schedule_layout = QGridLayout(schedule_group)

        # Поле 7: Дата и время начала
        schedule_layout.addWidget(QLabel("Начало записи:"), 0, 0)
        self.start_datetime_edit = QDateTimeEdit()
        self.start_datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(60))  # По умолчанию через 1 минуту
        self.start_datetime_edit.setCalendarPopup(True)  # Всплывающий календарь
        schedule_layout.addWidget(self.start_datetime_edit, 0, 1)

        # Поле 4: Интервал повторения
        schedule_layout.addWidget(QLabel("Интервал:"), 1, 0)
        interval_layout = QHBoxLayout()

        self.interval_value_spin = QSpinBox()
        self.interval_value_spin.setRange(1, 365)
        self.interval_value_spin.setValue(1)
        interval_layout.addWidget(self.interval_value_spin)

        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(["минут", "часов", "дней"])
        interval_layout.addWidget(self.interval_unit_combo)
        interval_layout.addStretch()

        schedule_layout.addLayout(interval_layout, 1, 1)

        main_layout.addWidget(schedule_group)

        # --- Кнопки ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def get_data(self):
        """Возвращает введенные данные в виде словаря."""
        # Конвертируем интервал в секунды
        unit = self.interval_unit_combo.currentText()
        multiplier = 1
        if unit == "минут":
            multiplier = 60
        elif unit == "часов":
            multiplier = 60 * 60
        elif unit == "дней":
            multiplier = 60 * 60 * 24

        interval_seconds = self.interval_value_spin.value() * multiplier

        return {
            "patient_name": self.patient_name_edit.text(),
            "device_sn": self.device_sn_edit.text(),
            "duration": self.duration_spin.value(),
            "interval": interval_seconds,
            "sample_rate": self.sample_rate_spin.value(),
            "format": self.format_combo.currentText(),
            "start_time": self.start_datetime_edit.dateTime().toString(Qt.ISODate)  # Сохраняем в ISO формате
        }


# Пример использования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ScheduleDialog()
    if dialog.exec() == QDialog.Accepted:
        schedule_data = dialog.get_data()
        print("Данные расписания:", schedule_data)
    sys.exit(app.exec())