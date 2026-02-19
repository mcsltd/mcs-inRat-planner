import datetime
from uuid import UUID

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QFont, QColor, QPen
from PySide6.QtWidgets import QTableView, QHeaderView, QStyledItemDelegate

from src.constants import MONTHS, ScheduleState
from src.db.database import connection
from src.db.models import Record
from src.structure import RecordData


class _DataTableModel(QAbstractTableModel):

    def __init__(self, description: list, data: list,  parent=None, *args):
        super().__init__(parent=parent)

        self.array_data: list = data
        self.columns = description

    # must be implemented: rowCount(), columnCount(), data(), headerData
    def headerData(self, section, orientation, /, role = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        return None

    def rowCount(self, /, parent = ...):
        return len(self.array_data)

    def columnCount(self, /, parent = ...):
        return len(self.columns)

    def data(self, index, /, role = ...):
        if len(self.array_data) == 0:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            value = self.array_data[index.row()][index.column()]
            if isinstance(value, datetime.datetime):
                value = self.convert_datetime_to_str(value.replace(microsecond=0))
                self.array_data[index.row()][index.column()] = value
            return value

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter

        return None

    def removeRow(self, row, /, parent = ...):
        self.removeRows(row, 1, parent)

    def removeRows(self, row, count, /, parent = ...):
        if 0 <= row < len(self.array_data):
            self.beginRemoveRows(parent, row, row + count)
            del self.array_data[row]
            self.endRemoveRows()

            self.dataChanged.emit(row, count)
            return True
        return False

    def convert_datetime_to_str(self, time: datetime.datetime):
        """
        Конвертация time (тип: datetime.datetime) в строку для отображения в таблице
        """
        try:
            date_part = f"{time.day:02d}-{MONTHS[time.month]}-{time.year}"
            time_part = time.strftime("%H:%M:%S")
            return f"{date_part} {time_part}"
        except (KeyError, AttributeError) as e:
            raise ValueError(f"Некорректный объект datetime: {e}")

class GenericTableWidget(QTableView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.description = []
        self.data_model = None
        self.data = []

        self.headerFont = QFont()
        self.headerFont.setBold(True)
        self.horizontalHeader().setFont(self.headerFont)

        self.setItemDelegate(_DataItemDelegate())

        self.setShowGrid(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)


        self.setStyleSheet("""
            QHeaderView::section {
                border: none;
                border-bottom: 2px solid #d0d0d0;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                color: #333;
            }
        """)

    def get_selected_index(self) -> None | list[QModelIndex]:
        """ Получение выбранных индексов """
        indexes = self.selectedIndexes()
        if not indexes:
            return None
        return indexes

    def get_selected_data(self) -> None | list:
        """ Получение данных в выбранной строке таблицы """
        selected_indexes = self.get_selected_index()
        if selected_indexes is None:
            return None

        index_row = selected_indexes[0].row()
        row_data = self.data_model.array_data[index_row]

        return row_data

    def setData(self,
                data: list, description: list) -> None:
        """ Установка колонок (description) и строк (data) в таблицу"""
        self.data = data
        self.description = description

        self.data_model = _DataTableModel(data=data, description=description)
        self.setModel(self.data_model)
        self.adjust_headers()

    def adjust_headers(self) -> None:
        """
        Регулировка колонок таблицы
        :return: None
        """
        if "id" in self.description:
            index = self.description.index("id")
            self.hideColumn(index)

        if "№" in self.description:
            index = self.description.index("№")
            self.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeMode.ResizeToContents)

    def modify_value_by_id(self, row_id: UUID, column_name: str, value: str) -> bool:
        """ Изменение значения в колонке по идентификатору и названию колонки """
        if not self.data_model or not self.data_model.array_data:
            return False

        if column_name not in self.description:
            return False

        column_index = self.description.index(column_name)
        row_index = -1
        if "id" in self.description:
            for r_idx, row_data in enumerate(self.data_model.array_data):
                if row_id in row_data:
                    row_index = r_idx
                    break

        if row_index == -1:
            return False

        model_index = self.data_model.index(row_index, column_index)
        self.data_model.array_data[row_index][column_index] = value
        self.data_model.dataChanged.emit(model_index, model_index, [Qt.ItemDataRole.DisplayRole])

        return True

    def get_selected_records_id(self) -> list | None:
        """Возврат выбранных ID в таблице Records"""
        if not hasattr(self.model(), "columns") or "id" not in self.model().columns:
            return None

        column_id = self.model().columns.index("id")

        selected_rows = {idx.row() for idx in self.selectedIndexes()}

        record_ids = []
        for row in selected_rows:
            index = self.model().index(row, column_id)
            record_id = self.model().data(index, Qt.ItemDataRole.DisplayRole)
            if record_id is not None:
                record_ids.append(record_id)

        return record_ids

    @connection
    def get_selected_records(self, session) -> list[RecordData]:
        """ Возврат путей выбранных записей """
        records = []

        record_ids = self.get_selected_records_id()
        for idx in record_ids:
            record = Record.find([Record.id == idx], session)
            if record is not None:
                record_data = record.to_dataclass()
                records.append(record_data)

        return records

class _DataItemDelegate(QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.border_color_rules = {
            ScheduleState.CONNECTION.value: QColor(255, 165, 0),
            ScheduleState.IN_QUEUE.value: QColor(255, 165, 0),
            ScheduleState.ACQUISITION.value: QColor(0, 255, 0),
        }

    def paint(self, painter, option, index, /):
        super().paint(painter, option, index)

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text in list(self.border_color_rules.keys()):
            painter.save()
            pen = QPen(self.border_color_rules[text])
            pen.setWidth(3)
            painter.setPen(pen)

            rect = option.rect
            painter.drawRect(rect)

            painter.restore()

    # def createEditor(self, parent, option, index, /):
    #     """ Возвращает виджет, используемый для изменения данных из модели,
    #      и может быть повторно реализован для настройки поведения редактирования """
    #     ...
    #
    # def setEditorData(self, editor, index, /):
    #     """ Предоставляет данные виджету для работы """
    #     ...
    #
    # def updateEditorGeometry(self, editor, option, index, /):
    #     """ Обеспечивает корректное отображение редактора по отношению к представлению элемента """
    #     ...
    #
    # def setModelData(self, editor, model, index, /):
    #     """ Возвращает обновленные данные в модель """
    #     ...