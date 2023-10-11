from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide2.QtGui import QColor


class BodiesModel(QAbstractListModel):  # A new model for the list
    def __init__(self, parent=None):
        super().__init__(parent)

        # Don't ever touch this directly ok thanks
        # (this is so we can inform the UI whenever we change this)
        self._body_storage = []

    def append(self, body):  # To add a body
        index_to_insert = len(self._body_storage)  # Gets body storage length
        self.beginInsertRows(QModelIndex(), index_to_insert, index_to_insert)  # Where in list we insert rows
        self._body_storage.append(body)  # When we truly add it
        self.endInsertRows()  # Telling QT done modifying stuff, pls update now UI

    def remove_at(self, index):  # To remove a body at a certain index.
        self.beginRemoveRows(QModelIndex(), index, index)  # Begin removing a certain body
        del self._body_storage[index]  # bye bye body
        self.endRemoveRows()  # Telling QT done modifying stuff.

    def clear(self):  # Empties body storage, a clear all button.
        self.beginResetModel()  # Tells Qt to forget everything and re-sync the UI from here
        self._body_storage = []
        self.endResetModel()  # The clearing.

    def rowCount(self, parent):  # This is how many elements we have in a list
        return len(self._body_storage)

    def flags(self, index):  # Tells us that all the balls are selectable and are enabled.
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, section, orientation, role):  # If a table, it has headers
        return "woah you will never see this"

    def data(self, index, role):  # Naming the ball
        if role == Qt.DisplayRole:
            return self._body_storage[index.row()].name  # Give the name.

        elif role == Qt.BackgroundColorRole:
            return QColor(self._body_storage[index.row()].color)  # Should give color next to the name of the body.

        elif role == Qt.TextColorRole:
            bg_color = QColor(self._body_storage[index.row()].color).toHsl()
            if bg_color.lightness() < 127:
                return QColor(255, 255, 255)  # This effectively generates the text colour.
            else:
                return QColor(0, 0, 0)

        else:
            return None

    def on_body_changed(self, index):
        self.dataChanged.emit(self.index(index, 0), self.index(index, 0))  # Informs Qt UI that a ball updated.

    # This is just convenience, but allows bodiesmodel[] instead of bodiesmodel._bodies_storage[]
    def __getitem__(self, item):
        return self._body_storage[item]

    def __len__(self):  # This gets the length of body storage
        return len(self._body_storage)
