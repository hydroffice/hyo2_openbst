import logging
from typing import Optional

from PySide2 import QtCore, QtWidgets

from hyo2.abc.app.qt_progress import QtProgress

logger = logging.getLogger(__name__)


class AbstractTab(QtWidgets.QMainWindow):

    def __init__(self, main_win: QtWidgets.QMainWindow, tab_name: Optional[str] = None):
        QtWidgets.QMainWindow.__init__(self)
        self.settings = QtCore.QSettings()

        self.main_win = main_win
        if not hasattr(main_win, "prj"):
            raise TypeError("Passed invalid reference to the main window: %s" % type(main_win))
        self.prj = self.main_win.prj
        self.tab_idx = -1
        self.progress = QtProgress(parent=self)

        if tab_name:
            self.tab_name = tab_name
        else:
            self.tab_name = "Tab"
        self.setWindowTitle(tab_name)

        self.setContentsMargins(0, 0, 0, 0)

        # add main frame and layout
        self.frame = QtWidgets.QFrame(parent=self)
        self.setCentralWidget(self.frame)
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.frame_layout)
