from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

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

        # Создаем кастомные кнопки
        yes_button = msg_box.addButton(yes_text, QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton(no_text, QMessageBox.ButtonRole.NoRole)

        if not btn_no:
            msg_box.removeButton(no_button)

        msg_box.setDefaultButton(yes_button)

        msg_box.exec()

        return msg_box.clickedButton() == yes_button