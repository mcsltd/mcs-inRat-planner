from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtGui import QIcon

from src.db.database import connection
from src.db.models import Experiment

from src.resources.v1.dlg_input_experiment import Ui_DlgInputExperiment
from src.structure import ExperimentData

PATH_TO_ICON = "resources/v1/icon_app.svg"

class DlgCreateExperiment(Ui_DlgInputExperiment, QDialog):

    def __init__(self, experiment_data: ExperimentData | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))

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