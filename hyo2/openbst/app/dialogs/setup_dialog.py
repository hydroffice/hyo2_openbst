import logging
import os
from typing import TYPE_CHECKING
from PySide2 import QtWidgets, QtGui, QtCore
from hyo2.openbst.app import app_info

if TYPE_CHECKING:
    from hyo2.openbst.lib.openbst import OpenBST

logger = logging.getLogger(__name__)


class SetupDialog(QtWidgets.QDialog):

    default_show_welcome_dialog = "True"
    default_key_show_mouse_patch = "True"
    default_key_max_undo_steps = 3

    def __init__(self, lib: 'OpenBST', parent=None):
        super().__init__(parent)
        self.lib = lib

        self.settings = QtCore.QSettings()
        self.setObjectName("SetupDialog")

        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Settings")
        self.setMinimumSize(QtCore.QSize(300, 240))
        self.setMaximumSize(QtCore.QSize(640, 4200))
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.set_tabs_icon_size(26)
        vbox.addWidget(self.tabs)

        # ### tab app ###

        self.tab_app = QtWidgets.QWidget()
        # noinspection PyArgumentList
        self.tab_app_idx = self.tabs.insertTab(0, self.tab_app,
                                               QtGui.QIcon(os.path.join(app_info.app_media_path, "app.png")), "")
        vbox_app = QtWidgets.QVBoxLayout()
        self.tab_app.setLayout(vbox_app)

        hbox = QtWidgets.QHBoxLayout()
        vbox_app.addLayout(hbox)
        show_welcome_lbl = QtWidgets.QLabel("Show welcome dialog:")
        hbox.addWidget(show_welcome_lbl)
        hbox.addStretch()
        self.show_welcome = QtWidgets.QCheckBox()
        is_checked = self.settings.value(app_info.key_show_welcome_dialog,
                                         self.default_show_welcome_dialog) == "True"
        self.show_welcome.setChecked(is_checked)
        # noinspection PyUnresolvedReferences
        self.show_welcome.stateChanged.connect(self.on_show_welcome)
        hbox.addWidget(self.show_welcome)

        hbox = QtWidgets.QHBoxLayout()
        vbox_app.addLayout(hbox)
        show_mouse_patch_lbl = QtWidgets.QLabel("Show area of mouse interaction:")
        hbox.addWidget(show_mouse_patch_lbl)
        hbox.addStretch()
        self.show_mouse_patch = QtWidgets.QCheckBox()
        is_checked = self.settings.value(app_info.key_show_mouse_patch,
                                         self.default_key_show_mouse_patch) == "True"
        self.show_mouse_patch.setChecked(is_checked)
        # noinspection PyUnresolvedReferences
        self.show_mouse_patch.stateChanged.connect(self.on_show_mouse_patch)
        hbox.addWidget(self.show_mouse_patch)

        hbox = QtWidgets.QHBoxLayout()
        vbox_app.addLayout(hbox)
        max_undo_steps_lbl = QtWidgets.QLabel("Maximum undo steps:")
        hbox.addWidget(max_undo_steps_lbl)
        hbox.addStretch()
        self.max_undo_steps = QtWidgets.QSpinBox()
        self.max_undo_steps.setRange(0, 9)
        max_undo_steps = self.settings.value(app_info.key_max_undo_steps,
                                             self.default_key_max_undo_steps)
        self.max_undo_steps.setValue(max_undo_steps)
        # noinspection PyUnresolvedReferences
        self.max_undo_steps.valueChanged.connect(self.on_max_undo_steps)
        hbox.addWidget(self.max_undo_steps)

        vbox_app.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox_app.addLayout(hbox)
        hbox.addStretch()
        button0 = QtWidgets.QPushButton()
        button0.setText("Reset")
        # noinspection PyUnresolvedReferences
        button0.clicked.connect(self.on_app_reset)
        hbox.addWidget(button0)
        hbox.addStretch()

        vbox_app.addStretch()

        # ### tab lib ###

        self.tab_lib = QtWidgets.QWidget()
        # noinspection PyArgumentList
        self.tab_lib_idx = self.tabs.insertTab(1, self.tab_lib,
                                               QtGui.QIcon(os.path.join(app_info.app_media_path, "lib.png")), "")

        vbox_lib = QtWidgets.QVBoxLayout()
        self.tab_lib.setLayout(vbox_lib)
        hbox = QtWidgets.QHBoxLayout()
        vbox_lib.addLayout(hbox)
        self.setup_viewer = QtWidgets.QTextEdit()
        self.setup_viewer.setReadOnly(True)
        self.setup_viewer.setText(self.lib.setup.info_str())
        self.setup_viewer.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        hbox.addWidget(self.setup_viewer)

    def set_tabs_icon_size(self, icon_size: int) -> None:
        self.tabs.setIconSize(QtCore.QSize(icon_size, icon_size))

    def on_show_welcome(self):
        checked = self.show_welcome.isChecked()
        logger.debug("show welcome: %s" % checked)
        if checked:
            self.settings.setValue(app_info.key_show_welcome_dialog, "True")
        else:
            self.settings.setValue(app_info.key_show_welcome_dialog, "False")

    def on_show_mouse_patch(self):
        checked = self.show_mouse_patch.isChecked()
        logger.debug("show mouse patch: %s" % checked)
        if checked:
            self.settings.setValue(app_info.key_show_mouse_patch, "True")
        else:
            self.settings.setValue(app_info.key_show_mouse_patch, "False")

    def on_max_undo_steps(self):
        max_undo_steps = self.max_undo_steps.value()
        logger.debug("max undo steps: %d" % max_undo_steps)
        self.settings.setValue(app_info.key_max_undo_steps, max_undo_steps)

    def on_app_reset(self):
        logger.debug("app settings reset")
        self.show_welcome.setChecked(self.default_show_welcome_dialog == "True")
        self.show_mouse_patch.setChecked(self.default_key_show_mouse_patch == "True")
        self.max_undo_steps.setValue(self.default_key_max_undo_steps)
