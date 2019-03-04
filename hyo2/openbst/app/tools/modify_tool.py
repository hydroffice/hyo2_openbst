import logging
import os
from typing import TYPE_CHECKING

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.app import app_info
from hyo2.openbst.app.tools.abstract_tool import AbstractTool

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from hyo2.figleaf.app.tabs.processing_tab import ProcessingTab

logger = logging.getLogger(__name__)


class ModifyTool(AbstractTool):

    def __init__(self, main_wdg='ProcessingTab', parent: QtWidgets.QWidget = None) -> None:
        super().__init__(main_wdg=main_wdg, parent=parent)

        self.setWindowTitle("Modify Tool")
        self.resize(320, 160)

        self.modify_algos = [
            "Gaussian Filter",
            "Median Filter"
        ]

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        label = QtWidgets.QLabel("Size in nodes: ")
        hbox.addWidget(label)
        self.size = QtWidgets.QSpinBox()
        self.size.setValue(20)
        self.size.setMinimum(1)
        self.size.setMaximum(9999)
        hbox.addWidget(self.size)
        self.radius = QtWidgets.QCheckBox("As radius")
        self.radius.setChecked(True)
        hbox.addWidget(self.radius)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        self.noise = QtWidgets.QCheckBox("Add random noise")
        self.noise.setChecked(True)
        hbox.addWidget(self.noise)
        hbox.addStretch()
        vbox.addSpacing(10)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        self.whole = QtWidgets.QCheckBox("Apply to all grid")
        self.whole.setChecked(False)
        hbox.addWidget(self.whole)
        hbox.addStretch()
        vbox.addSpacing(10)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        label = QtWidgets.QLabel("Approach: ")
        hbox.addWidget(label)
        self.algo = QtWidgets.QComboBox()
        self.algo.addItems(self.modify_algos)
        self.algo.setCurrentIndex(0)
        hbox.addWidget(self.algo)
        info_button = QtWidgets.QPushButton()
        hbox.addWidget(info_button)
        info_button.setFixedHeight(app_info.app_button_height)
        info_button.setAutoDefault(False)
        info_button.setIcon(QtGui.QIcon(os.path.join(app_info.app_media_path, 'small_info.png')))
        info_button.setToolTip('Open the manual page')
        # noinspection PyUnresolvedReferences
        info_button.clicked.connect(self.click_open_manual)
        hbox.addStretch()

        vbox.addStretch()

    # ### OTHER STUFF ###

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/figleaf/user_manual_2_3_4_modify_tool.html")

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.main_wdg.modify_act.setChecked(False)
        super().closeEvent(event)
