from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtGui import QIcon

from db.database import connection
from db.models import Experiment

from resources.v1.dlg_input_experiment import Ui_DlgInputExperiment
from structure import ExperimentData

PATH_TO_ICON = "resources/v1/icon_app.svg"

class DlgCreateExperiment(Ui_DlgInputExperiment, QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))

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
                        "Выберите другое названием для эксперимента."
            )
            return True
        return False

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
        exp_d = ExperimentData(name)
        return exp_d