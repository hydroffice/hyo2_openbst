import logging
import os
from PySide2 import QtGui, QtWidgets

from hyo2.openbst.app import app_info
from hyo2.openbst.app.bars.abstract_bar import AbstractBar
from hyo2.openbst.app.dialogs.current_project_dialog import CurrentProjectDialog

logger = logging.getLogger(__name__)


class FileProjectBar(AbstractBar):

    def __init__(self, main_win, main_tab, canvas, lib):
        super().__init__(main_tab=main_tab, main_win=main_win, canvas=canvas, lib=lib)
        self.setWindowTitle("Project")

        self.setMinimumWidth(40)

        # switch project
        tip = 'Switch project'
        self.switch_prj_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'prj_switch.png')),
                                                tip, self)
        # noinspection PyTypeChecker
        self.switch_prj_act.setShortcut('Alt+W')
        self.switch_prj_act.setStatusTip(tip)
        # noinspection PyUnresolvedReferences
        self.switch_prj_act.triggered.connect(self.on_switch_project)
        self.addAction(self.switch_prj_act)
        self.main_win.menu_file_project.addAction(self.switch_prj_act)

        # current project
        tip = 'Current project'
        self.current_prj_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'prj_info.png')),
                                                 tip, self)
        # noinspection PyTypeChecker
        self.current_prj_act.setShortcut('Alt+I')
        self.current_prj_act.setStatusTip(tip)
        # noinspection PyUnresolvedReferences
        self.current_prj_act.triggered.connect(self.on_current_project)
        self.addAction(self.current_prj_act)
        self.main_win.menu_file_project.addAction(self.current_prj_act)

    def on_switch_project(self):
        logger.debug("switch project")

        # noinspection PyArgumentList,PyCallByClass
        name, ret = QtWidgets.QInputDialog.getItem(self, "Switch project", "New or existing project name:",
                                                   self.lib.projects_list, current=0, editable=True)
        if not ret:
            return

        logger.debug("selected name: %s (%s)" % (name, ret))

    def on_current_project(self):
        logger.debug("show current project")
        current_project_dialog_dialog = CurrentProjectDialog(parent=self, lib=self.lib)
        current_project_dialog_dialog.exec_()
