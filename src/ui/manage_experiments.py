from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog

from src.config import PATH_TO_ICON
from src.resources.v1.widget_crud_experiment import Ui_WidgetCrudExperiment
from src.ui.settings_dialog import WidgetCfgExperiment, ConfigSignals


class ExperimentCRUDWidget(QDialog, Ui_WidgetCrudExperiment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QIcon(PATH_TO_ICON))

        self.signals = ConfigSignals(self)

        self.main_widget = WidgetCfgExperiment(self)
        self.verticalLayout.addWidget(self.main_widget)
