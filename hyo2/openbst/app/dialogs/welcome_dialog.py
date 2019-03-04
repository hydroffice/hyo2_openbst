import os
import sys
from PySide2 import QtCore, QtGui, QtWidgets

import logging

from hyo2.openbst.app import app_info

logger = logging.getLogger(__name__)


class WelcomeDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("WelcomeDialog")

        def refuse():
            sys.exit()

        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("Welcome!")
        self.setMinimumSize(QtCore.QSize(800, 600))
        self.setMaximumSize(QtCore.QSize(1200, 800))
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap(os.path.join(app_info.app_media_path, "welcome.png")))
        hbox.addWidget(logo)
        hbox.addStretch()

        vbox.addSpacing(10)

        text0 = QtWidgets.QLabel()
        text0.setOpenExternalLinks(True)
        vbox.addWidget(text0)
        text0.setText("""
        The Open Backscatter Toolchain (OpenBST) project aims to provide the community<br>
        with an open-source and metadata-rich modular implementation of a toolchain<br>
        dedicated to acoustic backscatter processing.<br>
        <br>
        The long-term goal is not to create processing tools that would compete<br>
        with available commercial solutions, but rather a set of open-source,<br>
        community-vetted, reference algorithms usable by both developers and users<br>
        for benchmarking their processing algorithms.<br>
        <br>
        <b>This tool should not be used in any manner contrary to this specific circumstance.</b><br>
        <br>
        For additional information, visit <a href=\"https://www.hydroffice.org/openbst/\">this link</a>.
        <br>
        """)
        # noinspection PyUnresolvedReferences
        text0.setAlignment(QtCore.Qt.AlignCenter)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button0 = QtWidgets.QPushButton()
        button0.setText("Accept")
        # noinspection PyUnresolvedReferences
        button0.clicked.connect(self.close)
        hbox.addWidget(button0)
        button1 = QtWidgets.QPushButton()
        button1.setText("Refuse")
        # noinspection PyUnresolvedReferences
        button1.clicked.connect(refuse)
        hbox.addWidget(button1)
        hbox.addStretch()
