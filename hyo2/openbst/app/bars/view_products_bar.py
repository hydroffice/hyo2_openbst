import logging
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc_context
from hyo2.openbst.app.dialogs.array_explorer.array_explorer import ArrayExplorer
from hyo2.openbst.app import app_info
from hyo2.openbst.app.bars.abstract_bar import AbstractBar
from hyo2.openbst.lib.plotting import Plotting

from PySide2 import QtGui, QtWidgets

logger = logging.getLogger(__name__)


class ViewProductsBar(AbstractBar):

    def __init__(self, main_win, processing_tab, canvas, prj):
        super().__init__(processing_tab=processing_tab, main_win=main_win, canvas=canvas, prj=prj)
        self.setWindowTitle("View Raster/Vector")

        # info
        tip = 'Show info about raster/vector'
        self.info_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'info_grid.png')),
                                          tip, self)
        # noinspection PyTypeChecker
        self.info_act.setShortcut('Alt+I')
        self.info_act.setStatusTip(tip)
        self.info_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.info_act.triggered.connect(self.on_info_raster)
        self.addAction(self.info_act)
        self.main_win.menu_view_products.addAction(self.info_act)

        # spreadsheet
        tip = 'View data spreadsheet'
        self.spreadsheet_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'spreadsheet.png')),
                                                 tip, self)
        # noinspection PyTypeChecker
        self.spreadsheet_act.setShortcut('Ctrl+S')
        self.spreadsheet_act.setStatusTip(tip)
        self.spreadsheet_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.spreadsheet_act.triggered.connect(self.on_data_spreadsheet)
        self.addAction(self.spreadsheet_act)
        self.main_win.menu_view_products.addAction(self.spreadsheet_act)

        # histo
        tip = 'Plot raster histogram'
        self.histo_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'histo_grid.png')),
                                           tip, self)
        # noinspection PyTypeChecker
        self.histo_act.setShortcut('Ctrl+H')
        self.histo_act.setStatusTip(tip)
        self.histo_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.histo_act.triggered.connect(self.on_histo_raster)
        self.addAction(self.histo_act)
        self.main_win.menu_view_products.addAction(self.histo_act)

    def on_info_raster(self) -> None:
        layer_key = self.processing_tab.current_layer_key()
        logger.debug("User wants to retrieve info from %s" % layer_key)

        msg = "Layer Key: %s\n\n%s" % (layer_key, self.prj.layers_dict[layer_key].info_str())
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Grid Info", msg, QtWidgets.QMessageBox.Ok)

    def on_data_spreadsheet(self) -> None:
        logger.debug("User wants to view raster data on a spreadsheet")
        d = ArrayExplorer(layer=self.processing_tab.current_layer(), parent=self,
                          with_menu=False, with_info_button=False, with_help_button=False)
        _ = d.exec_()

    def on_histo_raster(self) -> None:
        logger.debug("User wants to plot raster histogram")

        array = self.processing_tab.current_layer_array()

        min_range = np.nanmin(array)
        max_range = np.nanmax(array)
        med_value = np.nanmedian(array)
        avg_value = np.nanmean(array)
        arr_valid = np.isnan(array) == 0
        arr_flatten = array[arr_valid].flatten()

        with rc_context(app_info.plot_rc_context):

            delta = (max_range - min_range) * 0.02

            plt.ion()
            plt.figure("Histogram")

            fig_man = plt.get_current_fig_manager()
            fig_man.window.setWindowIcon(QtGui.QIcon(app_info.app_icon_path))

            n, bins, bin_patches = plt.hist(arr_flatten, bins=100, density=True,
                                            range=(min_range - delta * 5, max_range + delta * 5))
            plt.setp(bin_patches, 'facecolor', Plotting.blue_color, 'alpha', 0.75)

            plt.axvline(min_range, color='r', linestyle=':', label="min")
            plt.text(min_range + delta, 0.003, "%.2f" % min_range, color='r')

            plt.axvline(avg_value, color='y', linestyle=':', label="mean")
            plt.text(avg_value + delta, 0.003, "%.2f" % avg_value, color='y')

            plt.axvline(med_value, color='m', linestyle=':', label="median")
            plt.text(med_value + delta, 0.01, "%.2f" % med_value, color='m')

            plt.axvline(max_range, color='b', linestyle=':', label="max")
            plt.text(max_range + delta, 0.003, "%.2f" % max_range, color='b')

            plt.grid(True)
            plt.legend()
            plt.show()

        logger.debug("plotting raster histogram: done!")

    def raster_loaded(self):
        self.info_act.setEnabled(True)
        self.spreadsheet_act.setEnabled(True)
        self.histo_act.setEnabled(True)

    def raster_unloaded(self):
        self.info_act.setDisabled(True)
        self.spreadsheet_act.setDisabled(True)
        self.histo_act.setDisabled(True)

    def vector_loaded(self):
        self.info_act.setEnabled(True)
        self.spreadsheet_act.setEnabled(False)  # nothing to spreadsheet
        self.histo_act.setEnabled(False)  # nothing to histogram

    def vector_unloaded(self):
        self.info_act.setDisabled(True)
        self.spreadsheet_act.setDisabled(True)
        self.histo_act.setDisabled(True)
