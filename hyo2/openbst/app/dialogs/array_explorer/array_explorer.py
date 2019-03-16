from typing import Optional
import numpy as np
import os
import logging

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.openbst.app.dialogs.array_explorer.array_data_model import ArrayDataModel
from hyo2.openbst.lib.products.product_layer import ProductLayer

logger = logging.getLogger(__name__)


class ArrayExplorer(QtWidgets.QDialog):
    media = os.path.join(os.path.dirname(__file__), "media")

    def __init__(self, layer: ProductLayer, parent: Optional[QtWidgets.QWidget] = None,
                 with_menu: bool = False, with_info_button: bool = False, with_help_button: bool = False) -> None:
        super().__init__(parent)

        self.setWindowTitle('ArrayExplorer')
        self.resize(600, 400)
        self.with_menu = with_menu
        self.with_info_button = with_info_button
        self.with_help_button = with_help_button
        self._layer = layer
        self._arr = layer.array
        if (self._arr.ndim == 0) or (self._arr.ndim > 3):
            raise RuntimeError("Unsupported array shape: %d" % self._arr.ndim)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        if self.with_menu:
            self.layout().setMenuBar(QtWidgets.QMenuBar())
            self.file_menu = self.layout().menuBar().addMenu("File")
            self.view_menu = self.layout().menuBar().addMenu("View")
            self.edit_menu = self.layout().menuBar().addMenu("Edit")
            self.help_menu = self.layout().menuBar().addMenu("Help")

        self.top_layout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(self.top_layout)
        self.main_tb = QtWidgets.QToolBar("Main")
        self.main_tb.setIconSize(QtCore.QSize(32, 32))
        self.main_tb.setAutoFillBackground(True)
        self.top_layout.addWidget(self.main_tb)

        # Info
        if self.with_info_button:
            self.info_action = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'info.png')), "Info", self)
            self.info_action.setStatusTip("Show Info")
            # noinspection PyUnresolvedReferences
            self.info_action.triggered.connect(self.do_info)
            self.main_tb.addAction(self.info_action)
            if self.with_menu:
                self.file_menu.addAction(self.info_action)

        # Depth
        if self._arr.ndim == 3:
            self.main_tb.addSeparator()
            self.depth_label = QtWidgets.QLabel("Depth:")
            self.main_tb.addWidget(self.depth_label)
            self.depth_spin = QtWidgets.QSpinBox()
            self.depth_spin.setValue(0)
            self.depth_spin.setMinimum(0)
            self.depth_spin.setMaximum(self._arr.shape[2] - 1)
            # noinspection PyUnresolvedReferences
            self.depth_spin.valueChanged[int].connect(self.do_change_depth)
            self.main_tb.addWidget(self.depth_spin)

        # Locker
        self.main_tb.addSeparator()
        lock_icon = QtGui.QIcon()
        lock_icon.addFile(os.path.join(self.media, 'lock.png'), state=QtGui.QIcon.Off)
        lock_icon.addFile(os.path.join(self.media, 'unlock.png'), state=QtGui.QIcon.On)
        # noinspection PyTypeChecker
        self.lock_action = self.main_tb.addAction(lock_icon, "Lock", self.do_lock)
        self.lock_action.setCheckable(True)
        if self.with_menu:
            self.file_menu.addAction(self.lock_action)

        # Help
        if self.with_help_button:
            self.main_tb.addSeparator()
            # noinspection PyTypeChecker
            self.help_action = self.main_tb.addAction(
                QtGui.QIcon(os.path.join(self.media, 'help.png')), "Help", self.do_help)
            if self.with_menu:
                self.help_menu.addAction(self.help_action)

        self.main_wdg = QtWidgets.QSplitter(self)
        self.main_wdg.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.main_wdg)

        # ### LEFT ###

        self.left_wdg = QtWidgets.QWidget(self)
        self.left_wdg.setMinimumWidth(80)
        self.left_wdg.setMaximumWidth(120)
        self.main_wdg.addWidget(self.left_wdg)
        self.main_wdg.setStretchFactor(0, 1)

        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        self.left_wdg.setLayout(self.left_layout)
        self.left_layout.addStretch()
        self.left_label = QtWidgets.QLabel()
        self.left_label.setStyleSheet("font-size: small; color: rgba(25,115,200,255);")
        # noinspection PyUnresolvedReferences
        self.left_label.setAlignment(QtCore.Qt.AlignCenter)
        self.left_label.setText(self.array_info())
        self.left_layout.addWidget(self.left_label)
        self.left_layout.addStretch()

        # ### RIGHT ###

        self.right_wdg = QtWidgets.QWidget(self)
        # self.right_wdg.setAutoFillBackground(True)
        # right_palette = self.main_wdg.palette()
        # right_palette.setColor(self.main_wdg.backgroundRole(), QtCore.Qt.white)
        # self.right_wdg.setPalette(right_palette)
        self.main_wdg.addWidget(self.right_wdg)
        self.main_wdg.setStretchFactor(1, 5)

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_wdg.setLayout(self.right_layout)
        self.right_table = QtWidgets.QTableView()
        self.right_table.setObjectName("ArrayExplorerTable")
        # self.right_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.right_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.array_model = ArrayDataModel(layer=self._layer, parent=self)
        self.right_table.setModel(self.array_model)
        # self.right_table.resizeColumnsToContents()  # make things slow!!!
        self.right_layout.addWidget(self.right_table)

    @property
    def array(self) -> np.ndarray:
        return self._arr

    def array_info(self) -> str:
        if isinstance(self._arr, np.ndarray):
            txt = "%s\n" % (self._arr.shape,)
            txt += "%s" % (self._arr.dtype,)
        else:
            txt = "N/A"
        return txt

    def do_help(self) -> None:
        logger.debug("help")

    def do_info(self) -> None:
        logger.debug("info")

    def do_change_depth(self, depth):
        # logger.debug("change depth: %d" % depth)
        self.array_model.depth = depth
        # noinspection PyUnresolvedReferences
        self.array_model.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        # self.right_table.update()

    def do_lock(self):
        if self.lock_action.isChecked():
            msg = "Do you really want to manually edit the array data?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Spreadsheet", msg,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.lock_action.setChecked(False)
                return
            self.array_model.setEditable(True)
        else:
            self.array_model.setEditable(False)

    def array_modified(self):
        self.parent().update_plot_data()
