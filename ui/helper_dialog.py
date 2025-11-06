from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

class DialogHelper(QObject):
    @staticmethod
    def show_confirmation_dialog(parent, title, message, yes_text="Да", no_text="Нет"):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Question)

        # Создаем кастомные кнопки
        yes_button = msg_box.addButton(yes_text, QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton(no_text, QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(yes_button)

        msg_box.exec()

        return msg_box.clickedButton() == yes_button