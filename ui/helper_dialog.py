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
            icon: QMessageBox.Icon = QMessageBox.Icon.Information,
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
