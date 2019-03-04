import logging

from hyo2.openbst.lib.sources.layer import Layer
from PySide2 import QtCore, QtWidgets
import numpy as np
QVariant = lambda value=None: value

logger = logging.getLogger(__name__)


class ArrayDataModel(QtCore.QAbstractTableModel):

    def __init__(self, layer: Layer, parent: QtWidgets.QWidget):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._layer = layer
        self.array = layer.array
        self.editable = False
        self.depth = 0

        if (self.array.ndim == 0) or (self.array.ndim > 3):
            raise RuntimeError("Unsupported array shape: %d" % self.array.ndim)

        self.amp = "%s"

        self.is_float = False
        if self.array.dtype in [np.float32, np.float]:
            self.is_float = True
            self.amp = "%.3f"

        self.is_double = False
        if self.array.dtype in [np.float64, np.double]:
            self.is_double = True
            self.amp = "%.6f"

        self.is_integer = False
        if self.array.dtype in [ bool, np.int, np.int8, np.int16, np.int32, np.int64,
                                 np.uint, np.uint8, np.uint16, np.uint32, np.uint64, ]:
            self.is_integer = True
            self.amp = "%d"

    def setEditable(self, value: bool) -> None:
        self.editable = value

    def flags(self, index):
        flags = super(ArrayDataModel, self).flags(index)
        if self.editable:
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=None) -> int:
        return self.array.shape[0]

    def columnCount(self, parent=None) -> int:
        if self.array.ndim == 1:
            return 1
        return self.array.shape[1]

    def signalUpdate(self):
        """This is full update, not efficient"""
        # noinspection PyUnresolvedReferences
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(30, 30)

        if role == QtCore.Qt.DisplayRole:

            if orientation == QtCore.Qt.Horizontal:
                try:
                    return '%05d' % section
                except IndexError:
                    return QVariant()
            elif orientation == QtCore.Qt.Vertical:
                try:
                    return '%05d' % (self.array.shape[0] - 1 - section)
                except IndexError:
                    return QVariant()

        return QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        if role == QtCore.Qt.DisplayRole:

            if not index.isValid():
                return QVariant()

            if self.array.ndim == 1:
                return QVariant(self.amp % self.array[self.array.shape[0] - 1 - index.row()])

            elif self.array.ndim == 2:
                return QVariant(self.amp % self.array[self.array.shape[0] - 1 - index.row(), index.column()])

            return QVariant(self.amp % self.array[self.array.shape[0] - 1 - index.row(), index.column(), self.depth])

        return QVariant()

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        r = self.array.shape[0] - 1 - index.row()
        c = index.column()
        # test user input value
        try:
            if self.is_float or self.is_double:
                user_value = float(value)

            elif self.is_integer:
                user_value = int(value)

            else:
                logger.warning("assumed string: %s" % value)
                user_value = value

        except ValueError:
            msg = "invalid input: %s" % value
            QtWidgets.QMessageBox.critical(self.parent(), "Spreadsheet", msg, QtWidgets.QMessageBox.Ok)
            return False

        logger.debug("array(%d, %d) = %s" % (r, c, user_value))
        self._layer.store_undo_array()
        self.array[r, c] = user_value
        self._layer.modified = True
        delta = 5
        self._layer.plot.updated_layer_array(rect_slice=np.s_[r-delta:r+delta, c-delta:c+delta])
        self.parent().array_modified()
        return True
