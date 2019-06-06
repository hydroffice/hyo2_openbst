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
    from hyo2.openbst.lib.openbst import OpenBST

logger = logging.getLogger(__name__)


class ProductModifyTool(AbstractTool):

    def __init__(self, main_win: 'MainWindow', main_tab: 'MainTab', main_canvas: 'MainCanvas', lib: 'OpenBST') -> None:
        super().__init__(main_win=main_win, main_tab=main_tab, main_canvas=main_canvas, lib=lib)

        self.setWindowTitle("Modify Tool")
        self.resize(QtCore.QSize(320, 160))

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
    def click_open_manual(cls) -> None:
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/openbst/user_manual_2_tool_product_modify.html")

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.main_tab.edit_products_bar.modify_act.setChecked(False)
        super().closeEvent(event)
