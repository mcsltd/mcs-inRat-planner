from PySide6.QtCore import QAbstractTableModel, Qt


class DataTableModel(QAbstractTableModel):
    def __init__(self, column_names: list[str], parent=None, *args):
        super().__init__(parent=parent)

        self.data = []
        self.columns = column_names

    # must be implemented: rowCount(), columnCount(), data(), headerData

    def headerData(self, section, orientation, /, role = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        return None

    def rowCount(self, /, parent = ...):
        return len(self.data)

    def columnCount(self, /, parent = ...):
        return len(self.columns)

    def data(self, index, /, role = ...):

        if len(self.data) == 0:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            ...

    # def setData(self, index, value, /, role = ...):
        # must be implemented if models is editable
    #     ...



