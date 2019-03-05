import logging
import os
from typing import TYPE_CHECKING

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.app import app_info
from hyo2.openbst.app.tools.abstract_tool import AbstractTool

if TYPE_CHECKING:
    from hyo2.openbst.app.main_window import MainWindow
    from hyo2.openbst.app.main_tab import MainTab
    from hyo2.openbst.app.main_canvas import MainCanvas
    from hyo2.openbst.lib.project import Project

logger = logging.getLogger(__name__)


class ProductCloneTool(AbstractTool):

    def __init__(self, main_win: 'MainWindow', main_tab: 'MainTab', main_canvas: 'MainCanvas', prj: 'Project') -> None:
        super().__init__(main_win=main_win, main_tab=main_tab, main_canvas=main_canvas, prj=prj)

        self.setWindowTitle("Clone Tool")
        self.resize(320, 120)

        self.clone_algos = [
            "Triangle",
            "Bell",
            "Hill",
            "Plain",
            "Averaged",
            "Plain Noise",
            "Triangular Noise",
            "Bell-shaped Noise"
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
        label = QtWidgets.QLabel("Approach: ")
        hbox.addWidget(label)
        self.algo = QtWidgets.QComboBox()
        self.algo.addItems(self.clone_algos)
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
    def click_open_manual(cls) -> None:
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/openbst/user_manual_2_tool_product_clone.html")

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.main_tab.edit_products_bar.clone_act.setChecked(False)
        super().closeEvent(event)
