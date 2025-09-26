import logging

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QDialog
from sqlalchemy import insert, select

# scheduler
from constants import DESCRIPTION_COLUMN_HISTORY, DESCRIPTION_COLUMN_SCHEDULE, EXAMPLE_DATA_SCHEDULE, \
    EXAMPLE_DATA_HISTORY
from structure import DataSchedule
# ui
from ui.v1.main_window import Ui_MainWindow
from widgets import DlgCreateSchedule, DlgCreateExperiment
from tools.modview import GenericTableWidget

# database
from db.database import database
from db.models import Schedule, Experiment
from db.queries import get_experiments, add_schedule, get_schedules, add_device, add_object

logger = logging.getLogger(__name__)

EXPERIMENTS = ["Эксперимент-X",]

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat Planner")

        # create view for table Schedule and History
        self.tableModelSchedule = GenericTableWidget()
        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=EXAMPLE_DATA_SCHEDULE, )
        self.labelSchedule.setText(f"Расписание (всего: {len(EXAMPLE_DATA_SCHEDULE)})")

        self.tableModelHistory = GenericTableWidget()
        self.tableModelHistory.setData(description=DESCRIPTION_COLUMN_HISTORY, data=EXAMPLE_DATA_HISTORY)
        self.labelHistory.setText(f"Записей (всего: {len(EXAMPLE_DATA_HISTORY)})")

        # add tables
        self.verticalLayoutHistory.addWidget(self.tableModelHistory)
        self.verticalLayoutSchedule.addWidget(self.tableModelSchedule)

        self.pushButtonAddExperiment.clicked.connect(self.addExperiment)
        self.pushButtonAddSchedule.clicked.connect(self.addSchedule)
        # ToDo: self.pushButtonUpdateSchedule.clicked.connect(...)
        # ToDo: self.pushButtonDeleteSchedule.clicked.connect(self.deleteScheduleFromDB)
        # ToDo: self.pushButtonShowRecords.clicked.connect(...)

        self.updateContentTableSchedule()
        # self.updateContentTableHistory()

    # Experiment
    def addExperiment(self) -> None:
        dlg = DlgCreateExperiment()
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            exp = dlg.getExperiment()
            logger.debug(f"Add experiment={exp} into db")
            with database.engine.connect() as conn:
                stmt = insert(Experiment).values(name=exp)
                conn.execute(stmt)
                conn.commit()
        return


    # Schedule
    def addSchedule(self) -> None:
        logger.info("Adding a new schedule")

        dlg = DlgCreateSchedule(experiments=get_experiments())
        code = dlg.exec()
        if code == QDialog.DialogCode.Accepted:
            schedule: DataSchedule = dlg.getSchedule()

            if schedule is None:
                logger.error("An error occurred while creating the schedule")
                return

            logger.info(f"Add Object in DB: id={add_object(name=schedule.patient)}")
            logger.info(f"Add Device in DB: id={add_device(sn=schedule.device_sn, model=schedule.device_model)}")
            logger.info(f"Add Schedule in DB: id={add_schedule(schedule)}")

            # fill table Schedule
            self.updateContentTableSchedule()

            logger.info("Schedule created successfully")

    def updateContentTableSchedule(self):
        logger.info("Set data in the Schedule table")
        table_data = []

        result = get_schedules()

        # ToDo: rewrite it
        for row in result:
            column_1_5 = row[:5]
            status = ("None",)
            column_7_8 = row[7:8]
            column_9_11 = 4 * (0,)
            params = "; ".join([str(v) for v in row[-2:]]) + " Гц"
            data = list(column_1_5 + status + column_7_8 + column_9_11)
            data.append(params)

            table_data.append(data)

        self.tableModelSchedule.setData(description=DESCRIPTION_COLUMN_SCHEDULE, data=table_data)
        # update label Schedule
        self.labelSchedule.setText(f"Расписание (всего: {len(table_data)})")

    def updateSchedule(self) -> None:
        logger.info("The contents of the Schedule table have been updated")
        pass

    def deleteSchedule(self) -> None:
        logger.info("Deleting a schedule")
        pass

    # History
    def updateTableHistory(self):
        logger.info("The contents of the History table have been updated")
        pass

    def updateContentTableHistory(self):
        # update label History
        self.labelHistory.setText(f"История (всего: 0)")

    def _get_row_as_dict(self, table: QTableView, index: QModelIndex) -> dict:
        model = table.model()
        data: dict = {}
        for idx_col in range(model.columnCount()):
            key = model.headerData(idx_col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            data[key] = model.index(index.row(), idx_col).data(Qt.ItemDataRole.DisplayRole)
        return data


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    # window.show()
    app.exec()