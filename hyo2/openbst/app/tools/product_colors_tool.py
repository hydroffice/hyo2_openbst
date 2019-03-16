import logging
import os
from typing import TYPE_CHECKING

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.lib.products.product_plotting import ProductPlotting
from hyo2.openbst.app import app_info
from hyo2.openbst.app.tools.abstract_tool import AbstractTool

if TYPE_CHECKING:
    from hyo2.openbst.app.main_window import MainWindow
    from hyo2.openbst.app.main_tab import MainTab
    from hyo2.openbst.app.main_canvas import MainCanvas
    from hyo2.openbst.lib.project import Project

logger = logging.getLogger(__name__)


class ProductColorsTool(AbstractTool):

    def __init__(self, main_win: 'MainWindow', main_tab: 'MainTab', main_canvas: 'MainCanvas', prj: 'Project') -> None:
        super().__init__(main_win=main_win, main_tab=main_tab, main_canvas=main_canvas, prj=prj)

        self.setWindowTitle("Colors Tool")
        self.resize(480, 100)

        field_sz = 50

        # build ui

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        label = QtWidgets.QLabel("Colormap: ")
        hbox.addWidget(label)
        self.cm = QtWidgets.QComboBox()
        self.cm.addItems(list(ProductPlotting.cmaps.keys()))
        self.cm.setCurrentIndex(0)
        # noinspection PyUnresolvedReferences
        self.cm.currentIndexChanged.connect(self.on_apply_colormap)
        hbox.addWidget(self.cm)
        label = QtWidgets.QLabel("Min: ")
        hbox.addWidget(label)
        self.min = QtWidgets.QLineEdit("0.0")
        validator = QtGui.QDoubleValidator(-99999.0, 99999.0, 9, self.min)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.min.setValidator(validator)
        # noinspection PyUnresolvedReferences
        self.min.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.min.setReadOnly(False)
        self.min.setFixedWidth(field_sz)
        # noinspection PyUnresolvedReferences
        self.min.returnPressed.connect(self.on_apply_range)
        # noinspection PyUnresolvedReferences
        self.min.textChanged.connect(self.on_modified_range)
        hbox.addWidget(self.min)
        label = QtWidgets.QLabel("Max: ")
        hbox.addWidget(label)
        self.max = QtWidgets.QLineEdit("0.0")
        validator = QtGui.QDoubleValidator(-99999.0, 99999.0, 9, self.max)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.max.setValidator(validator)
        # noinspection PyUnresolvedReferences
        self.max.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.max.setReadOnly(False)
        self.max.setFixedWidth(field_sz)
        # noinspection PyUnresolvedReferences
        self.max.returnPressed.connect(self.on_apply_range)
        # noinspection PyUnresolvedReferences
        self.max.textChanged.connect(self.on_modified_range)
        hbox.addWidget(self.max)
        hbox.addStretch()
        self.cmap_reset = QtWidgets.QPushButton("Reset")
        self.cmap_reset.setAutoDefault(False)
        # noinspection PyUnresolvedReferences
        self.cmap_reset.clicked.connect(self.on_reset_colormap)
        # noinspection PyUnresolvedReferences
        self.cmap_reset.clicked.connect(self.on_reset_range)
        hbox.addWidget(self.cmap_reset)
        info_button = QtWidgets.QPushButton()
        hbox.addWidget(info_button)
        info_button.setFixedHeight(app_info.app_button_height)
        info_button.setAutoDefault(False)
        info_button.setIcon(QtGui.QIcon(os.path.join(app_info.app_media_path, 'small_info.png')))
        info_button.setToolTip('Open the manual page')
        # noinspection PyUnresolvedReferences
        info_button.clicked.connect(self.click_open_manual)

        vbox.addSpacing(12)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addSpacing(3)
        self.shade_lbl = QtWidgets.QLabel("Shading: ")
        hbox.addWidget(self.shade_lbl)
        self.shade = QtWidgets.QCheckBox("")
        self.shade.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.shade.stateChanged.connect(self.on_checked_shading)
        hbox.addWidget(self.shade)
        self.shade_exag_lbl = QtWidgets.QLabel("-> Exag: ")
        hbox.addWidget(self.shade_exag_lbl)
        self.shade_exag = QtWidgets.QLineEdit("1.0")
        validator = QtGui.QDoubleValidator(1.0, 99999.0, 9, self.shade_exag)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.shade_exag.setValidator(validator)
        # noinspection PyUnresolvedReferences
        self.shade_exag.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.shade_exag.setReadOnly(False)
        self.shade_exag.setDisabled(True)
        self.shade_exag.setFixedWidth(field_sz)
        # noinspection PyUnresolvedReferences
        self.shade_exag.returnPressed.connect(self.on_apply_shade)
        # noinspection PyUnresolvedReferences
        self.shade_exag.textChanged.connect(self.on_modified_shade)
        hbox.addWidget(self.shade_exag)
        self.shade_az_lbl = QtWidgets.QLabel("Az: ")
        hbox.addWidget(self.shade_az_lbl)
        self.shade_az = QtWidgets.QLineEdit("0.0")
        validator = QtGui.QDoubleValidator(0.0, 360.0, 9, self.shade_az)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.shade_az.setValidator(validator)
        # noinspection PyUnresolvedReferences
        self.shade_az.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.shade_az.setReadOnly(False)
        self.shade_az.setDisabled(True)
        self.shade_az.setFixedWidth(field_sz)
        # noinspection PyUnresolvedReferences
        self.shade_az.returnPressed.connect(self.on_apply_shade)
        # noinspection PyUnresolvedReferences
        self.shade_az.textChanged.connect(self.on_modified_shade)
        hbox.addWidget(self.shade_az)
        self.shade_elev_lbl = QtWidgets.QLabel("Elev: ")
        hbox.addWidget(self.shade_elev_lbl)
        self.shade_elev = QtWidgets.QLineEdit("0.0")
        validator = QtGui.QDoubleValidator(0.0, 90.0, 9, self.shade_elev)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.shade_elev.setValidator(validator)
        # noinspection PyUnresolvedReferences
        self.shade_elev.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.shade_elev.setReadOnly(False)
        self.shade_elev.setDisabled(True)
        self.shade_elev.setFixedWidth(field_sz)
        # noinspection PyUnresolvedReferences
        self.shade_elev.returnPressed.connect(self.on_apply_shade)
        # noinspection PyUnresolvedReferences
        self.shade_elev.textChanged.connect(self.on_modified_shade)
        hbox.addWidget(self.shade_elev)
        hbox.addStretch()
        self.shade_reset = QtWidgets.QPushButton("Reset")
        self.shade_reset.setAutoDefault(False)
        self.shade_reset.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.shade_reset.clicked.connect(self.on_reset_shade)
        hbox.addWidget(self.shade_reset)
        info_button = QtWidgets.QPushButton()
        hbox.addWidget(info_button)
        info_button.setFixedHeight(app_info.app_button_height)
        info_button.setAutoDefault(False)
        info_button.setIcon(QtGui.QIcon(os.path.join(app_info.app_media_path, 'small_info.png')))
        info_button.setToolTip('Open the manual page')
        # noinspection PyUnresolvedReferences
        info_button.clicked.connect(self.click_open_manual)

        vbox.addStretch()

    def show(self) -> None:
        layer = self.main_tab.current_layer()

        # ### COLORMAP ###

        # noinspection PyUnresolvedReferences
        self.cm.currentIndexChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.min.textChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.max.textChanged.disconnect()

        self.cm.setCurrentText(ProductPlotting.cmaps.inv[layer.plot.cmap])
        self.min.setText("%.3f" % layer.plot.array_min)
        self.max.setText("%.3f" % layer.plot.array_max)

        # noinspection PyUnresolvedReferences
        self.cm.currentIndexChanged.connect(self.on_apply_colormap)
        # noinspection PyUnresolvedReferences
        self.min.textChanged.connect(self.on_modified_range)
        # noinspection PyUnresolvedReferences
        self.max.textChanged.connect(self.on_modified_range)

        # ### SHADING ###

        # noinspection PyUnresolvedReferences
        self.shade.stateChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.shade_exag.returnPressed.disconnect()
        # noinspection PyUnresolvedReferences
        self.shade_exag.textChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.shade_az.returnPressed.disconnect()
        # noinspection PyUnresolvedReferences
        self.shade_az.textChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.shade_elev.returnPressed.disconnect()
        # noinspection PyUnresolvedReferences
        self.shade_elev.textChanged.disconnect()

        if layer.plot.is_shadable():
            self.shade_lbl.setEnabled(True)
            self.shade.setEnabled(True)

            self.shade.setChecked(layer.plot.with_shading)
            self.shade_exag_lbl.setEnabled(layer.plot.with_shading)
            self.shade_exag.setEnabled(layer.plot.with_shading)
            self.shade_az_lbl.setEnabled(layer.plot.with_shading)
            self.shade_az.setEnabled(layer.plot.with_shading)
            self.shade_elev_lbl.setEnabled(layer.plot.with_shading)
            self.shade_elev.setEnabled(layer.plot.with_shading)
            self.shade_reset.setDisabled(layer.plot.with_shading)

            self.shade_exag.setText("%.1f" % layer.plot.shade_exag)
            self.shade_az.setText("%.1f" % layer.plot.shade_az)
            self.shade_elev.setText("%.1f" % layer.plot.shade_elev)

        else:
            self.shade.setChecked(False)

            self.shade_lbl.setDisabled(True)
            self.shade.setDisabled(True)
            self.shade_exag_lbl.setDisabled(True)
            self.shade_exag.setDisabled(True)
            self.shade_az_lbl.setDisabled(True)
            self.shade_az.setDisabled(True)
            self.shade_elev_lbl.setDisabled(True)
            self.shade_elev.setDisabled(True)
            self.shade_reset.setDisabled(True)

            self.shade_exag.setText("1.0")
            self.shade_az.setText("0.0")
            self.shade_elev.setText("1.0")

        # noinspection PyUnresolvedReferences
        self.shade.stateChanged.connect(self.on_checked_shading)
        # noinspection PyUnresolvedReferences
        self.shade_exag.returnPressed.connect(self.on_apply_shade)
        # noinspection PyUnresolvedReferences
        self.shade_exag.textChanged.connect(self.on_modified_shade)
        # noinspection PyUnresolvedReferences
        self.shade_az.returnPressed.connect(self.on_apply_shade)
        # noinspection PyUnresolvedReferences
        self.shade_az.textChanged.connect(self.on_modified_shade)
        # noinspection PyUnresolvedReferences
        self.shade_elev.returnPressed.connect(self.on_apply_shade)
        # noinspection PyUnresolvedReferences
        self.shade_elev.textChanged.connect(self.on_modified_shade)

        super().show()

    # ### COLORMAP ###

    def on_apply_colormap(self) -> None:
        cmap_key = self.cm.currentText()
        logger.debug("changed colormap: %s" % cmap_key)

        layer = self.main_tab.current_layer()
        layer.plot.cmap = ProductPlotting.cmaps[cmap_key]
        self.main_tab.update_plot_cmap()

    def on_reset_colormap(self) -> None:
        layer = self.main_tab.current_layer()
        layer.plot.init_cmap()
        self.main_tab.update_plot_cmap()
        reset_cmap = ProductPlotting.cmaps.inv[layer.plot.cmap]
        logger.debug("reset colormap: %s" % reset_cmap)
        self.cm.setCurrentText(reset_cmap)

    def on_modified_range(self) -> None:
        self.min.setStyleSheet("background-color: rgba(255, 255, 153, 255);")
        self.max.setStyleSheet("background-color: rgba(255, 255, 153, 255);")

    def on_apply_range(self) -> None:
        logger.debug("apply range")
        self.min.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.max.setStyleSheet("background-color: rgba(255, 255, 255, 255);")

        min_value = float(self.min.text())
        max_value = float(self.max.text())
        layer = self.main_tab.current_layer()

        if min_value >= max_value:
            msg = "The selected values are invalid: %f and %f" % (min_value, max_value)
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Invalid Range", msg, QtWidgets.QMessageBox.Ok)

            self.min.setText("%.3f" % layer.plot.array_min)
            self.max.setText("%.3f" % layer.plot.array_max)
            return

        layer.plot.array_min = min_value
        layer.plot.array_max = max_value
        self.main_tab.update_plot_range()

    def on_reset_range(self) -> None:
        logger.debug("reset range")
        layer = self.main_tab.current_layer()
        self.min.setText("%.3f" % layer.array_min)
        self.max.setText("%.3f" % layer.array_max)
        self.on_apply_range()

    # ### SHADING ###

    def on_checked_shading(self) -> None:
        logger.debug("on checked shading: %s" % self.shade.isChecked())
        if self.shade.isChecked():
            self.shade_exag_lbl.setEnabled(True)
            self.shade_az_lbl.setEnabled(True)
            self.shade_elev_lbl.setEnabled(True)
            self.shade_exag.setEnabled(True)
            self.shade_az.setEnabled(True)
            self.shade_elev.setEnabled(True)
            self.shade_reset.setEnabled(True)

        else:
            self.shade_exag_lbl.setEnabled(False)
            self.shade_az_lbl.setEnabled(False)
            self.shade_elev_lbl.setEnabled(False)
            self.shade_exag.setEnabled(False)
            self.shade_az.setEnabled(False)
            self.shade_elev.setEnabled(False)
            self.shade_reset.setEnabled(False)

        self.on_apply_shade()

    def on_modified_shade(self) -> None:
        self.shade_exag.setStyleSheet("background-color: rgba(255, 255, 153, 255);")
        self.shade_az.setStyleSheet("background-color: rgba(255, 255, 153, 255);")
        self.shade_elev.setStyleSheet("background-color: rgba(255, 255, 153, 255);")

    def on_apply_shade(self) -> None:
        logger.debug("apply shade")
        self.shade_exag.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.shade_az.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.shade_elev.setStyleSheet("background-color: rgba(255, 255, 255, 255);")

        layer = self.main_tab.current_layer()
        layer.plot.with_shading = self.shade.isChecked()
        layer.plot.shade_exag = float(self.shade_exag.text())
        layer.plot.shade_az = float(self.shade_az.text())
        layer.plot.shade_elev = float(self.shade_elev.text())
        layer.plot.apply_shading()

        self.main_tab.update_shading()

    def on_reset_shade(self) -> None:
        logger.debug("reset shade")

        layer = self.main_tab.current_layer()
        layer.plot.reset_shading_settings()

        self.shade.setChecked(layer.plot.with_shading)

        self.shade_exag.setText("%.1f" % layer.plot.shade_exag)
        self.shade_az.setText("%.1f" % layer.plot.shade_az)
        self.shade_elev.setText("%.1f" % layer.plot.shade_elev)

        self.on_apply_shade()

    # ### OTHER STUFF ###

    @classmethod
    def click_open_manual(cls) -> None:
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/openbst/user_manual_2_tool_product_colors.html")

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.main_tab.edit_products_bar.colors_act.setChecked(False)
        super().closeEvent(event)
