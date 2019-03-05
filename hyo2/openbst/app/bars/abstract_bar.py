import logging
from PySide2 import QtCore, QtWidgets
from hyo2.openbst.app import app_info

logger = logging.getLogger(__name__)


class AbstractBar(QtWidgets.QToolBar):

    def __init__(self, main_win, processing_tab, canvas, prj):
        super().__init__(parent=processing_tab)
        self.main_win = main_win
        self.processing_tab = processing_tab
        self.canvas = canvas
        self.prj = prj

        self.settings = QtCore.QSettings()

        icon_size = QtCore.QSize(app_info.app_toolbars_icon_size, app_info.app_toolbars_icon_size)
        self.setIconSize(icon_size)
