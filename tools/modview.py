from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class DataTableModel(QAbstractTableModel):
    def __init__(self, column_names: list[str], data: list[list],  parent=None, *args):
        super().__init__(parent=parent)

        self.arraydata: list[list] = data
        self.columns = column_names

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

    # must be implemented if models is editable
    # def setData(self, index, value, /, role = ...):
    #     ...



