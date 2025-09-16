import datetime

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView


class _DataTableModel(QAbstractTableModel):
    def __init__(self, description: list, data: list,  parent=None, *args):
        super().__init__(parent=parent)

        self.arraydata: list[list] = data
        self.columns = description

    # must be implemented: rowCount(), columnCount(), data(), headerData

    def headerData(self, section, orientation, /, role = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        return None

    def rowCount(self, /, parent = ...):
        return len(self.arraydata)

    def columnCount(self, /, parent = ...):
        return len(self.columns)

    def data(self, index, /, role = ...):
        if len(self.arraydata) == 0:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if type(self.arraydata[index.row()][index.column()]) is datetime.datetime:
                self.arraydata[index.row()][index.column()] = self.arraydata[index.row()][index.column()].time().replace(microsecond=0)
                self.arraydata[index.row()][index.column()] = str(self.arraydata[index.row()][index.column()])

            return self.arraydata[index.row()][index.column()]

        return None

    def removeRow(self, row, /, parent = ...):
        self.removeRows(row, 1, parent)

    def removeRows(self, row, count, /, parent = ...):
        if 0 <= row < len(self.arraydata):
            self.beginRemoveRows(parent, row, row + count)
            del self.arraydata[row]
            self.endRemoveRows()

            self.dataChanged.emit(row, count)
            return True
        return False


class GenericTableWidget(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = []
        self.description = []

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

    def setData(self, data, description):
        self.data = data
        self.description = description

        self.data_model = _DataTableModel(data=data, description=description)
        self.setModel(self.data_model)
