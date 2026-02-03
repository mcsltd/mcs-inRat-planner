from PySide6.QtWidgets import QMessageBox, QDialog, QWidget
from PySide6.QtGui import QIcon, QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from db.database import connection
from db.models import Experiment

from resources.v1.dlg_input_experiment import Ui_DlgInputExperiment
from structure import ExperimentData

PATH_TO_ICON = "resources/v1/icon_app.svg"

class DlgCreateExperiment(Ui_DlgInputExperiment, QDialog):

    MAX_LENGTH_EXPERIMENT = 30

    def __init__(self, experiment_data: ExperimentData | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))

        pattern = r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-_\.\,]*$'
        input_validator = QRegularExpressionValidator(QRegularExpression(pattern))
        self.lineEditExperiment.setValidator(input_validator)
        self.lineEditExperiment.setToolTip("Запрещены символы: {}[]@#$;^*-=|\\/'?%\"!`")
        self.lineEditExperiment.setMaxLength(self.MAX_LENGTH_EXPERIMENT)
        self.lineEditExperiment.textChanged.connect(self.on_text_changed)

        self.default_experiment = experiment_data
        if self.default_experiment is not None:
            self.lineEditExperiment.setText(self.default_experiment.name)

    @connection
    def _is_experiment_exists(self, session) -> bool:
        """ Проверка есть ли такой эксперимент в базе данных """
        name = self.lineEditExperiment.text().strip()
        if not name:  # Добавляем проверку на пустое имя
            self.show_error_message(
                title="Ошибка создания эксперимента",
                message="Название эксперимента не может быть пустым."
            )
            return True

        experiment = Experiment.find([Experiment.name == name], session)
        if experiment:
            self.show_error_message(
                title="Ошибка создания эксперимента",
                message="Эксперимент с похожим названием уже существует.\n"
                        "Выберите другое название для эксперимента."
            )
            return True
        return False

    def on_text_changed(self):
        name = self.lineEditExperiment.text()
        if len(name) == self.MAX_LENGTH_EXPERIMENT:
            self.highlight_field(self.lineEditExperiment)
            self.show_error_message(
                title="Предупреждение",
                message=f"Название слишком длинное. Используйте не более {self.MAX_LENGTH_EXPERIMENT} символов.")
        else:
            self.clear_highlight(self.lineEditExperiment)
        return None

    def show_error_message(self, title, message):
        """ Вывод окна с предупреждением о том что невозможно создать расписание """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def getExperiment(self) -> ExperimentData | None:
        """ Возврат данные об эксперименте в формате dataclass """
        if self._is_experiment_exists():
            return None

        name = self.lineEditExperiment.text().strip()
        if self.default_experiment is not None:
            self.default_experiment.name = name
            return self.default_experiment

        exp_d = ExperimentData(name)
        return exp_d

    @staticmethod
    def highlight_field(field: QWidget):
        """ Подсветка поля с ошибкой """
        field.setStyleSheet("border: 1px solid red; background-color: #FFE6E6;")

    @staticmethod
    def clear_highlight(field: QWidget):
        """ Убрать подсветку """
        field.setStyleSheet("")