from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox, QDialog, QPushButton, QLabel, QHBoxLayout, QVBoxLayout


class DialogHelper(QObject):
    @staticmethod
    def show_confirmation_dialog(
            parent, title, message, yes_text="Да", no_text="Нет",
            icon: QMessageBox.Icon=QMessageBox.Icon.Question,

            btn_no: bool = True
    ):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)

        yes_button = msg_box.addButton(yes_text, QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton(no_text, QMessageBox.ButtonRole.NoRole)

        if not btn_no:
            msg_box.removeButton(no_button)

        msg_box.setDefaultButton(yes_button)
        msg_box.exec()
        return msg_box.clickedButton() == yes_button

    @staticmethod
    def show_action_dialog(
            parent, title, message, yes_text="Ok", action_text="Ручной режим",
            icon: QMessageBox.Icon = QMessageBox.Icon.NoIcon,
    ):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)

        action_button = msg_box.addButton(action_text, QMessageBox.ButtonRole.ActionRole)
        yes_button = msg_box.addButton(yes_text, QMessageBox.ButtonRole.YesRole)

        msg_box.setDefaultButton(yes_button)
        msg_box.setDefaultButton(action_button)

        msg_box.exec()
        return msg_box.clickedButton() == action_button


class ConfirmManualModeDialog(QDialog):
    """ Диалоговое окно выбора перехода в ручной режим управления устройством """
    manual_mode_selected = Signal()
    exit_selected = Signal()

    def __init__(self, parent, title: str, message: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setWindowTitle(title)
        self.setModal(True)

        font = QFont()
        font.setPointSize(10)

        self._result = False
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.info_label = QLabel(message)
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.info_label.setFont(font)
        layout.addWidget(self.info_label)

        button_layout = QHBoxLayout()

        self.pushBtnConfirmManual = QPushButton("В ручной режим")
        self.pushBtnExit = QPushButton("Выйти")

        # Подключаем сигналы
        self.pushBtnConfirmManual.clicked.connect(self.on_manual_mode_clicked)
        self.pushBtnExit.clicked.connect(self.on_exit_clicked)

        button_layout.addStretch()
        button_layout.addWidget(self.pushBtnConfirmManual)
        button_layout.addWidget(self.pushBtnExit)

        layout.addLayout(button_layout)

    def on_manual_mode_clicked(self):
        """ переход в ручной режим """
        self._result = True
        self.manual_mode_selected.emit()
        self.accept()

    def on_exit_clicked(self):
        """ отмена перехода в ручной режим"""
        self._result = False
        self.exit_selected.emit()
        self.reject()

    def get_result(self) -> bool:
        """ возврат результата """
        return self._result

    @staticmethod
    def show_action_dialog(parent, title: str, message: str) -> bool:
        """ cтатический метод для вызова диалога """
        dialog = ConfirmManualModeDialog(parent, title, message)
        result = dialog.exec()

        if result == QDialog.Accepted:
            return True
        else:
            return False

