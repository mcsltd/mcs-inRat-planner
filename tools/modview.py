import datetime

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView


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
            if type(self.array_data[index.row()][index.column()]) is datetime.datetime:
                self.array_data[index.row()][index.column()] = str(self.array_data[index.row()][index.column()].replace(microsecond=0))
            return self.array_data[index.row()][index.column()]

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


class GenericTableWidget(QTableView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = []
        self.description = []

        self.headerFont = QFont()
        self.headerFont.setBold(True)
        self.horizontalHeader().setFont(self.headerFont)

        self.setShowGrid(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # выбирать только строки
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

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

    def setData(self, data, description):
        self.data = data
        self.description = description

        self.data_model = _DataTableModel(data=data, description=description)
        self.setModel(self.data_model)

        if "id" in self.description:
            index = self.description.index("id")
            self.hideColumn(index)
