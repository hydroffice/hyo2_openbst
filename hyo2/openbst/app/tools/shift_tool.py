import logging
import math
import os
from typing import TYPE_CHECKING

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.openbst.app.tools.abstract_tool import AbstractTool
from hyo2.openbst.app import app_info
from hyo2.abc.lib.helper import Helper

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from hyo2.openbst.app.tabs.processing_tab import ProcessingTab

logger = logging.getLogger(__name__)


class ShiftTool(AbstractTool):

    def __init__(self, main_wdg='ProcessingTab', parent: QtWidgets.QWidget = None) -> None:
        super().__init__(main_wdg=main_wdg, parent=parent)

        self.setWindowTitle("Shift Tool")
        self.resize(240, 100)

        field_sz = 50

        # build ui

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        label = QtWidgets.QLabel("Shift: ")
        hbox.addWidget(label)
        self.shift = QtWidgets.QLineEdit("0.0")
        validator = QtGui.QDoubleValidator(-99999.0, 99999.0, 9, self.shift)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.shift.setValidator(validator)
        self.shift.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.shift.setReadOnly(False)
        self.shift.setFixedWidth(field_sz)
        # noinspection PyUnresolvedReferences
        self.shift.returnPressed.connect(self.on_apply_shift)
        # noinspection PyUnresolvedReferences
        self.shift.textChanged.connect(self.on_modified_shift)
        hbox.addWidget(self.shift)
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

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/figleaf/user_manual_2_3_2_shift_tool.html")

    def on_modified_shift(self):
        self.shift.setStyleSheet("background-color: rgba(255, 255, 153, 255);")

    def on_apply_shift(self):
        logger.debug("apply shift")
        self.shift.setStyleSheet("background-color: rgba(255, 255, 255, 255);")

        shift_value = float(self.shift.text())
        if math.isclose(shift_value, 0.0):
            self.shift.setText("0.0")
            msg = 'First set a shift value different than zero!'
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Null Shift", msg, QtWidgets.QMessageBox.Ok)
            return

        logger.debug("applying shift: %s" % shift_value)

        layer = self.main_wdg.current_layer()
        layer.shift(value=shift_value)

        self.main_wdg.update_plot_data()

        # noinspection PyUnresolvedReferences
        self.shift.returnPressed.disconnect()
        # noinspection PyUnresolvedReferences
        self.shift.textChanged.disconnect()

        self.shift.setText("0.0")

        # noinspection PyUnresolvedReferences
        self.shift.returnPressed.connect(self.on_apply_shift)
        # noinspection PyUnresolvedReferences
        self.shift.textChanged.connect(self.on_modified_shift)

        msg = 'A shift value of %.3f was applied!' % shift_value
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Shift Applied", msg, QtWidgets.QMessageBox.Ok)

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.main_wdg.edit_products_bar.shift_act.setChecked(False)
        super().closeEvent(event)
