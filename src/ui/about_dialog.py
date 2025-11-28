from PySide6.QtWidgets import (QApplication, QWidget,
                               QVBoxLayout, QHBoxLayout, QLabel, QDialog,)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

from src.config import PATH_TO_ICON_MCS

FONT = "Arial"

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("О программе")
        self.setModal(True)
        self.setFixedSize(600, 400)

        # Основной layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)

        image_label = QLabel()
        try:
            pixmap = QPixmap(PATH_TO_ICON_MCS)
            if pixmap.isNull():
                pixmap = QPixmap(200, 200)
                pixmap.fill(Qt.lightGray)
        except:
            pixmap = QPixmap(200, 200)
            pixmap.fill(Qt.lightGray)

        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        # image_label.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")

        left_layout.addWidget(image_label)
        left_widget.setLayout(left_layout)

        # Правая часть - информация
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignTop)

        # Название программы
        title_label = QLabel("InRat Planner")
        title_font = QFont(FONT)
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        # title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        # Описание программы
        description_label = QLabel(
            "Программное обеспечение для записи ЭКГ мелких животных\nв форматах EDF, WFDB по расписанию")
        description_font = QFont()
        description_font.setPointSize(11)
        description_label.setFont(description_font)
        # description_label.setStyleSheet("color: #34495e; line-height: 1.4;")
        # description_label.setWordWrap(True)

        # Версия (бета)
        version_label = QLabel("Версия v.0.0.1 - beta")
        version_font = QFont("Arial")
        version_font.setPointSize(10)
        # version_font.setBold(True)
        version_label.setFont(version_font)
        # version_label.setStyleSheet("color: #e74c3c; margin-top: 10px;")

        # Отступ
        right_layout.addStretch()

        # Название компании (в самом низу)
        company_label = QLabel("© 2025 ООО \"Медицинские Компьютерные системы\"")
        company_font = QFont(FONT)
        company_font.setPointSize(9)
        company_label.setFont(company_font)
        # company_label.setStyleSheet("color: #7f8c8d; margin-top: 20px;")

        email_label = QLabel("<a href='https://mks.ru/ru'>https://mks.ru/ru</a>")
        email_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        email_label.setOpenExternalLinks(True)
        email_font = QFont(FONT)
        email_font.setPointSize(9)
        email_label.setFont(company_font)

        right_layout.addWidget(title_label)
        right_layout.addWidget(description_label)
        right_layout.addWidget(version_label)
        right_layout.addStretch()
        right_layout.addWidget(company_label)
        right_layout.addWidget(email_label)

        right_widget.setLayout(right_layout)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication()
    wind = AboutDialog()
    wind.show()
    app.exec()
