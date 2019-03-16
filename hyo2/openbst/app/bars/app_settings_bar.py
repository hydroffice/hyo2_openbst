import logging
import os

from hyo2.openbst.app import app_info
from hyo2.openbst.app.bars.abstract_bar import AbstractBar
from hyo2.openbst.app.dialogs.settings_dialog import SettingsDialog

from PySide2 import QtGui, QtWidgets

logger = logging.getLogger(__name__)


class AppSettingsBar(AbstractBar):

    def __init__(self, main_win, main_tab, canvas, prj):
        super().__init__(main_tab=main_tab, main_win=main_win, canvas=canvas, prj=prj)
        self.setWindowTitle("App Settings")

        tip = 'Show settings'
        self.show_settings_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'settings.png')),
                                                   tip, self)
        self.show_settings_act.setStatusTip(tip)
        # noinspection PyUnresolvedReferences
        self.show_settings_act.triggered.connect(self.on_show_settings)
        self.addAction(self.show_settings_act)
        self.main_win.menu_setup.addAction(self.show_settings_act)

    def on_show_settings(self):
        logger.debug("show settings")
        settings_dialog = SettingsDialog(parent=self)
        settings_dialog.exec_()
