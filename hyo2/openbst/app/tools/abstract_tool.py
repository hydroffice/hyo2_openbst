import logging
from typing import TYPE_CHECKING

from PySide2 import QtCore, QtWidgets

if TYPE_CHECKING:
    from hyo2.openbst.app.main_window import MainWindow
    from hyo2.openbst.app.main_tab import MainTab
    from hyo2.openbst.app.main_canvas import MainCanvas
    from hyo2.openbst.lib.project import Project

logger = logging.getLogger(__name__)


class AbstractTool(QtWidgets.QDialog):

    def __init__(self, main_win: 'MainWindow', main_tab: 'MainTab', main_canvas: 'MainCanvas', prj: 'Project') -> None:
        super().__init__(parent=main_tab)
        self.main_win = main_win
        self.main_tab = main_tab
        self.main_canvas = main_canvas
        self.prj = prj

        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setMinimumSize(160, 80)

    def show(self) -> None:
        """To show the tool within the main tab"""
        point = QtCore.QPoint(self.main_tab.rect().right() - self.width(), self.main_tab.rect().top() + 30)
        global_point = self.main_tab.mapToGlobal(point)
        self.move(global_point)
        super().show()
