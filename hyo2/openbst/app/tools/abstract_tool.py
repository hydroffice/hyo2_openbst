from PySide2 import QtCore, QtWidgets
import logging

logger = logging.getLogger(__name__)


class AbstractTool(QtWidgets.QDialog):

    def __init__(self, main_wdg, parent=None):
        super().__init__(parent)
        self.main_wdg = main_wdg
        self.main_win = self.main_wdg.main_win
        self.prj = self.main_win.prj

        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setMinimumSize(160, 80)

    def show(self):
        point = QtCore.QPoint(self.main_wdg.rect().right() - self.width(), self.main_wdg.rect().top() + 30)
        global_point = self.main_wdg.mapToGlobal(point)
        self.move(global_point)
        super().show()
