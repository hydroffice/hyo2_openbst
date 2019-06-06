import logging
import os
from typing import TYPE_CHECKING
from PySide2 import QtWidgets, QtGui, QtCore
from hyo2.openbst.app import app_info

if TYPE_CHECKING:
    from hyo2.openbst.lib.openbst import OpenBST

logger = logging.getLogger(__name__)


class CurrentProjectDialog(QtWidgets.QDialog):

    def __init__(self, lib: 'OpenBST', parent=None):
        super().__init__(parent)
        self.lib = lib

        self.settings = QtCore.QSettings()
        self.setObjectName("CurrentProjectDialog")

        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Current Project")
        self.setMinimumSize(QtCore.QSize(300, 240))
        self.setMaximumSize(QtCore.QSize(640, 4200))
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.set_tabs_icon_size(26)
        vbox.addWidget(self.tabs)

        # ### tab info ###

        self.tab_info = QtWidgets.QWidget()
        # noinspection PyArgumentList
        self.tab_info_idx = self.tabs.insertTab(0, self.tab_info,
                                                QtGui.QIcon(os.path.join(app_info.app_media_path, "info.png")), "")

        vbox_info = QtWidgets.QVBoxLayout()
        self.tab_info.setLayout(vbox_info)
        hbox = QtWidgets.QHBoxLayout()
        vbox_info.addLayout(hbox)
        self.setup_viewer = QtWidgets.QTextEdit()
        self.setup_viewer.setReadOnly(True)
        self.setup_viewer.setText(self.lib.prj.info_str())
        self.setup_viewer.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        hbox.addWidget(self.setup_viewer)

    def set_tabs_icon_size(self, icon_size: int) -> None:
        self.tabs.setIconSize(QtCore.QSize(icon_size, icon_size))
