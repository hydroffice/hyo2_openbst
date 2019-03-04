from PySide2 import QtCore, QtWidgets

import logging

from hyo2.openbst.app import app_info

logger = logging.getLogger(__name__)


class SettingsDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QtCore.QSettings()
        self.setObjectName("SettingsDialog")

        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("OpenBST Settings")
        self.setMinimumSize(QtCore.QSize(200, 180))
        self.setMaximumSize(QtCore.QSize(400, 280))
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        show_welcome_lbl = QtWidgets.QLabel("Show welcome dialog:")
        hbox.addWidget(show_welcome_lbl)
        hbox.addStretch()
        self.show_welcome = QtWidgets.QCheckBox()
        is_checked = self.settings.value(app_info.key_show_welcome_dialog, "True") == "True"
        self.show_welcome.setChecked(is_checked)
        hbox.addWidget(self.show_welcome)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        show_mouse_patch_lbl = QtWidgets.QLabel("Show area of mouse interaction:")
        hbox.addWidget(show_mouse_patch_lbl)
        hbox.addStretch()
        self.show_mouse_patch = QtWidgets.QCheckBox()
        is_checked = self.settings.value(app_info.key_show_mouse_patch, "True") == "True"
        self.show_mouse_patch.setChecked(is_checked)
        hbox.addWidget(self.show_mouse_patch)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        max_undo_steps_lbl = QtWidgets.QLabel("Maximum undo steps:")
        hbox.addWidget(max_undo_steps_lbl)
        hbox.addStretch()
        self.max_undo_steps = QtWidgets.QSpinBox()
        self.max_undo_steps.setRange(0, 99)
        max_undo_steps = self.settings.value(app_info.key_max_undo_steps,  3)
        self.max_undo_steps.setValue(max_undo_steps)
        hbox.addWidget(self.max_undo_steps)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button0 = QtWidgets.QPushButton()
        button0.setText("Apply")
        # noinspection PyUnresolvedReferences
        button0.clicked.connect(self.on_apply)
        hbox.addWidget(button0)
        button1 = QtWidgets.QPushButton()
        button1.setText("Cancel")
        # noinspection PyUnresolvedReferences
        button1.clicked.connect(self.on_cancel)
        hbox.addWidget(button1)
        hbox.addStretch()

    def on_apply(self):
        logger.debug("on apply")
        
        if self.show_welcome.isChecked():
            self.settings.setValue(app_info.key_show_welcome_dialog, "True")
        else:
            self.settings.setValue(app_info.key_show_welcome_dialog, "False")

        if self.show_mouse_patch.isChecked():
            self.settings.setValue(app_info.key_show_mouse_patch, "True")
        else:
            self.settings.setValue(app_info.key_show_mouse_patch, "False")

        self.settings.setValue(app_info.key_max_undo_steps, self.max_undo_steps.value())
            
        self.close()

    def on_cancel(self):
        logger.debug("on cancel")
        self.close()
