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


class ProductEraseTool(AbstractTool):

    def __init__(self, main_win: 'MainWindow', main_tab: 'MainTab', main_canvas: 'MainCanvas', lib: 'OpenBST') -> None:
        super().__init__(main_win=main_win, main_tab=main_tab, main_canvas=main_canvas, lib=lib)

        self.setWindowTitle("Erase Tool")
        self.resize(QtCore.QSize(320, 120))

        self.erase_algos = [
            "Plain",
            "Triangle",
            "Bell",
            "Hill"
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
        # self.size.setFont(GuiSettings.console_font())
        hbox.addWidget(self.size)
        self.radius = QtWidgets.QCheckBox("As radius")
        self.radius.setChecked(True)
        hbox.addWidget(self.radius)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        self.all_layers_lbl = QtWidgets.QLabel("Apply to all the layers from the same input: ")
        hbox.addWidget(self.all_layers_lbl)
        self.all_layers = QtWidgets.QCheckBox("")
        self.all_layers.setChecked(False)
        hbox.addWidget(self.all_layers)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        self.algo_lbl = QtWidgets.QLabel("Approach: ")
        hbox.addWidget(self.algo_lbl)
        self.algo = QtWidgets.QComboBox()
        self.algo.addItems(self.erase_algos)
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

    def show(self) -> None:
        layer = self.main_tab.current_layer()

        if layer.is_vector() and not layer.is_raster():
            self.algo_lbl.setDisabled(True)
            self.algo.setDisabled(True)
            self.all_layers_lbl.setDisabled(True)
            self.all_layers.setDisabled(True)
        else:
            self.algo_lbl.setEnabled(True)
            self.algo.setEnabled(True)
            self.all_layers_lbl.setEnabled(True)
            self.all_layers.setEnabled(True)

        super().show()

    # ### OTHER STUFF ###

    @classmethod
    def click_open_manual(cls) -> None:
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/openbst/user_manual_2_tool_product_erase.html")

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.main_tab.edit_products_bar.erase_act.setChecked(False)
        super().closeEvent(event)
