import logging
import os

import numpy as np
from PySide2 import QtCore, QtGui, QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc_context
import matplotlib.pyplot as plt
from matplotlib import image
from matplotlib import patches

from hyo2.abc.lib.helper import Helper

from hyo2.openbst.app.tabs.abstract_tab import AbstractTab
from hyo2.openbst.app import app_info
from hyo2.figleaf.lib.sources.format import FormatType
from hyo2.openbst.lib.sources.layer_type import LayerType
from hyo2.openbst.lib.sources.layer import EraseType, FilterType, CloneType, Layer
from hyo2.openbst.lib.plotting import Plotting
from hyo2.openbst.app.dialogs.array_explorer.array_explorer import ArrayExplorer
from hyo2.openbst.app.dialogs.settings_dialog import SettingsDialog
from hyo2.openbst.app.tabs.navigation_toolbar import NavToolbar
from hyo2.openbst.app.tools.shift_tool import ShiftTool
from hyo2.openbst.app.tools.colors_tool import ColorsTool
from hyo2.openbst.app.tools.erase_tool import EraseTool
from hyo2.openbst.app.tools.modify_tool import ModifyTool
from hyo2.openbst.app.tools.clone_tool import CloneTool

matplotlib.use('Qt5Agg')
matplotlib.rcParams['axes.formatter.useoffset'] = False
logger = logging.getLogger(__name__)


class ProcessingTab(AbstractTab):

    def __init__(self, main_win, tab_name="Processing Tab"):
        AbstractTab.__init__(self, main_win=main_win, tab_name=tab_name)

        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        icon_size = QtCore.QSize(app_info.app_toolbars_icon_size, app_info.app_toolbars_icon_size)

        # empty arrays
        self.nan_arr = np.zeros((1, 1), dtype=np.float32)
        self.nan_arr[:] = np.nan

        # ### FILE BAR ###

        self.file_bar = self.addToolBar('File')
        self.file_bar.setIconSize(icon_size)
        self.file_bar.setMinimumWidth(480)

        # load raster
        tip = 'Load raster'
        self.load_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'add_grid.png')),
                                          tip, self)
        # noinspection PyTypeChecker
        self.load_act.setShortcut('Alt+L')
        self.load_act.setStatusTip(tip)
        # noinspection PyUnresolvedReferences
        self.load_act.triggered.connect(self.on_load_raster)
        self.file_bar.addAction(self.load_act)
        self.main_win.menu_file.addAction(self.load_act)

        # layers
        tip = 'Layers tool'
        self.layers_combo = QtWidgets.QComboBox(self)
        self.layers_combo.setToolTip(tip)
        self.layers_combo.setStatusTip(tip)
        self.layers_combo.setDisabled(True)
        self.layers_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layers_combo.setMaximumWidth(360)
        # noinspection PyUnresolvedReferences
        self.layers_combo.currentIndexChanged.connect(self.on_layers_combo)
        self.file_bar.addWidget(self.layers_combo)

        # unload
        tip = 'Unload raster'
        self.unload_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'remove_grid.png')),
                                            tip, self)
        # noinspection PyTypeChecker
        self.unload_act.setShortcut('Alt+U')
        self.unload_act.setStatusTip(tip)
        self.unload_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.unload_act.triggered.connect(self.on_unload_raster)
        self.file_bar.addAction(self.unload_act)
        self.main_win.menu_file.addAction(self.unload_act)

        self.file_bar.addSeparator()

        # save
        tip = 'Save raster'
        self.save_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'save_grid.png')),
                                          tip, self)
        # noinspection PyTypeChecker
        self.save_act.setShortcut('Alt+S')
        self.save_act.setStatusTip(tip)
        self.save_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.save_act.triggered.connect(self.on_save_raster)
        self.file_bar.addAction(self.save_act)
        self.main_win.menu_file.addAction(self.save_act)

        # output
        tip = 'Open output folder'
        self.open_output_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'open_output.png')),
                                                 tip, self)
        self.open_output_act.setStatusTip(tip)
        # self.open_output_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.open_output_act.triggered.connect(self.on_open_output_folder)
        self.file_bar.addAction(self.open_output_act)
        self.main_win.menu_file.addAction(self.open_output_act)

        self.file_bar.addSeparator()

        # settings
        tip = 'Show settings'
        self.show_settings_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'settings.png')),
                                                   tip, self)
        self.show_settings_act.setStatusTip(tip)
        # noinspection PyUnresolvedReferences
        self.show_settings_act.triggered.connect(self.on_show_settings)
        self.file_bar.addAction(self.show_settings_act)
        self.main_win.menu_setup.addAction(self.show_settings_act)

        # ### VIEW TOOLBAR ###

        self.view_bar = self.addToolBar('View')
        self.view_bar.setIconSize(icon_size)

        # info
        tip = 'Show info about raster'
        self.info_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'info_grid.png')),
                                          tip, self)
        # noinspection PyTypeChecker
        self.info_act.setShortcut('Alt+I')
        self.info_act.setStatusTip(tip)
        self.info_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.info_act.triggered.connect(self.on_info_raster)
        self.view_bar.addAction(self.info_act)
        self.main_win.menu_view.addAction(self.info_act)

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
        self.view_bar.addAction(self.spreadsheet_act)
        self.main_win.menu_view.addAction(self.spreadsheet_act)

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
        self.view_bar.addAction(self.histo_act)
        self.main_win.menu_view.addAction(self.histo_act)

        # ### EDIT TOOLBAR ###

        self.edit_bar = self.addToolBar('Edit')
        self.edit_bar.setIconSize(icon_size)

        # colormap
        tip = 'Colors tool'
        self.colors_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'colors.png')),
                                            tip, self)
        # noinspection PyTypeChecker
        self.colors_act.setShortcut('Alt+C')
        self.colors_act.setStatusTip(tip)
        self.colors_act.setDisabled(True)
        self.colors_act.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.colors_act.triggered.connect(self.on_colors_tool)
        self.edit_bar.addAction(self.colors_act)
        self.main_win.menu_edit.addAction(self.colors_act)

        self.edit_bar.addSeparator()

        # shift
        tip = 'Shift tool'
        self.shift_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'plus_or_minus.png')),
                                           tip, self)
        # noinspection PyTypeChecker
        self.shift_act.setShortcut('Alt+S')
        self.shift_act.setStatusTip(tip)
        self.shift_act.setDisabled(True)
        self.shift_act.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.shift_act.triggered.connect(self.on_shift_tool)
        self.edit_bar.addAction(self.shift_act)
        self.main_win.menu_edit.addAction(self.shift_act)

        # erase
        tip = 'Erase tool'
        self.erase_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'erase.png')),
                                           tip, self)
        # noinspection PyTypeChecker
        self.erase_act.setShortcut('Alt+E')
        self.erase_act.setStatusTip(tip)
        self.erase_act.setDisabled(True)
        self.erase_act.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.erase_act.triggered.connect(self.on_erase_tool)
        self.edit_bar.addAction(self.erase_act)
        self.main_win.menu_edit.addAction(self.erase_act)

        # modify
        tip = 'Modify tool'
        self.modify_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'modify.png')),
                                            tip, self)
        # noinspection PyTypeChecker
        self.modify_act.setShortcut('Alt+M')
        self.modify_act.setStatusTip(tip)
        self.modify_act.setDisabled(True)
        self.modify_act.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.modify_act.triggered.connect(self.on_modify_tool)
        self.edit_bar.addAction(self.modify_act)
        self.main_win.menu_edit.addAction(self.modify_act)

        # clone
        tip = 'Clone tool'
        self.clone_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'clone.png')),
                                           tip, self)
        # noinspection PyTypeChecker
        self.clone_act.setShortcut('Alt+C')
        self.clone_act.setStatusTip(tip)
        self.clone_act.setDisabled(True)
        self.clone_act.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.clone_act.triggered.connect(self.on_clone_tool)
        self.edit_bar.addAction(self.clone_act)
        self.main_win.menu_edit.addAction(self.clone_act)

        self.edit_bar.addSeparator()

        # undo
        tip = 'Undo latest change'
        self.undo_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'undo.png')),
                                          tip, self)
        # noinspection PyTypeChecker
        self.undo_act.setShortcut('Ctrl+U')
        self.undo_act.setStatusTip(tip)
        self.undo_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.undo_act.triggered.connect(self.on_undo)
        self.edit_bar.addAction(self.undo_act)
        self.main_win.menu_edit.addAction(self.undo_act)

        # ### CANVAS ###
        self.colorbar = None
        self.mat_ax = None
        self.shd_ax = None
        self.fts_ax = None
        self.cln_x = list()
        self.cln_y = list()
        self.cln_ax = None
        self.mouse_ax = None
        self.mouse_patch = patches.Rectangle(xy=(0, 0), width=100, height=100, fill=False,
                                             edgecolor=Plotting.magenta_color, linestyle=":", linewidth=1.0)
        self.mouse_patch.set_visible(False)

        self.plot_layout = QtWidgets.QHBoxLayout()
        self.frame_layout.addLayout(self.plot_layout)

        with rc_context(app_info.plot_rc_context):
            self.f = Figure()
            self.f.patch.set_alpha(0.0)
            self.c = FigureCanvas(self.f)
            self.c.setParent(self.frame)
            # noinspection PyUnresolvedReferences
            self.c.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c.setFocus()
            self.plot_layout.addWidget(self.c)

            # axes
            self.data_ax = self.f.add_subplot(111)

            self.c.mpl_connect('resize_event', self.on_resize)
            self.c.mpl_connect('key_press_event', self.on_key_press)
            self.c.mpl_connect('button_press_event', self.on_mouse_press)
            self.c.mpl_connect('motion_notify_event', self.on_mouse_move)
            self.c.mpl_connect('pick_event', self.on_pick)
            self.c.mpl_connect('axes_enter_event', self.on_enter_axes)
            self.c.mpl_connect('axes_leave_event', self.on_leave_axes)

        # navigation
        self.nav = NavToolbar(canvas=self.c, parent=self.frame)
        self.frame_layout.addWidget(self.nav)

        # ### TOOLS ###
        self.colors_tool = ColorsTool(main_wdg=self, parent=self)
        self.shift_tool = ShiftTool(main_wdg=self, parent=self)
        self.erase_tool = EraseTool(main_wdg=self, parent=self)
        self.modify_tool = ModifyTool(main_wdg=self, parent=self)
        self.clone_tool = CloneTool(main_wdg=self, parent=self)

        self.on_empty_draw()

    # ### ICON SIZE ###

    def toolbars_icon_size(self) -> int:
        return self.file_bar.iconSize().height()

    def set_toolbars_icon_size(self, icon_size: int) -> None:
        self.file_bar.setIconSize(QtCore.QSize(icon_size, icon_size))

    # ### DRAG&DROP ###

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """Drop files directly onto the widget"""
        if e.mimeData().hasUrls:
            # noinspection PyUnresolvedReferences
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()

            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():

                dropped_path = str(url.toLocalFile())
                dropped_path = os.path.abspath(dropped_path).replace("\\", "/")
                logger.debug("dropped path: %s" % dropped_path)

                if os.path.isdir(dropped_path):
                    msg = 'Drag-and-drop is not currently possible with a folder!\n\n' \
                          'Dropped path: %s\n' % dropped_path
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Drag-and-drop Error", msg, QtWidgets.QMessageBox.Ok)
                    return

                if os.path.splitext(dropped_path)[-1] in [".bag", ".tif", ".tiff", ".asc", ]:
                    self.load_raster(path=dropped_path)

                else:
                    msg = 'Drag & drop is currently only possible with the following file extensions:\n' \
                          '- BAG: .bag -> bathymetry + uncertainty\n' \
                          '- GeoTiff: .tif, .tiff -> (assumed) backscatter mosaic\n' \
                          '- ASCII Grid: .asc + .prj -> user prompted for type selection\n\n' \
                          'Dropped path:\n' \
                          '%s' % dropped_path
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Input Error", msg, QtWidgets.QMessageBox.Ok)

        else:
            e.ignore()

    # ### PLOT INTERACTION ###

    def on_resize(self, event):
        fig_ratio = event.width / event.height
        x_min, x_max = self.data_ax.get_xlim()
        x_range = x_max - x_min
        y_min, y_max = self.data_ax.get_ylim()
        y_range = y_max - y_min
        data_ratio = x_range / y_range

        ratio = fig_ratio / data_ratio
        delta = (x_range * ratio - x_range) / 2.0
        # logger.debug("resizing: %f, %f" % (x_min, x_max))
        # logger.debug("resizing: %f (ratio: %f)" % (delta, ratio))
        self.data_ax.set_xlim(left=(x_min - delta), right=(x_max + delta))

    # noinspection PyMethodMayBeStatic
    def on_key_press(self, event):
        """Manage press event"""
        logger.debug("pressed key: %s" % event.key)

    def on_mouse_move(self, event):
        """Manage mouse move event"""
        has_layers = self.prj.has_layers()
        # logger.debug("moved mouse: %s [has layers: %s]" % (event.button, has_layers))
        if not has_layers:
            return

        is_checked = self.settings.value(app_info.key_show_mouse_patch, "True") == "True"
        if not is_checked:
            return

        visible = False
        radius = 0
        if self.erase_tool.isVisible():
            visible = True
            radius = self.erase_tool.size.value()
        elif self.modify_tool.isVisible():
            visible = True
            radius = self.modify_tool.size.value()
        elif self.clone_tool.isVisible():
            visible = True
            radius = self.clone_tool.size.value()

        if visible:
            # logger.debug("visible")
            if (event.xdata is not None) and (event.ydata is not None):
                layer = self.current_layer()
                dx_2, dy_2 = layer.dcdr2dxdy(dc=radius, dr=radius)
                self.mouse_patch.xy = event.xdata - dx_2, event.ydata - dy_2
                self.mouse_patch.set_width(dx_2 * 2)
                self.mouse_patch.set_height(dy_2 * 2)
                self.mouse_patch.set_visible(True)
                self.c.draw_idle()
        else:
            # logger.debug("not visible")
            self.mouse_patch.set_visible(False)
            self.c.draw_idle()

    def on_mouse_press(self, event):
        """Manage mouse press event"""
        has_layers = self.prj.has_layers()
        logger.debug("pressed mouse: %s [has layers: %s]" % (event.button, has_layers))
        if not has_layers:
            return

        if event.button == 1:
            return

        if event.button == 3:

            if len(self.cln_x) != 0:
                logger.debug("cleared cloning point: (%f, %f)" % (self.cln_x[0], self.cln_y[0]))
                self.cln_x = list()
                self.cln_y = list()

        elif event.button == 2:

            self.cln_x = [event.xdata, ]
            self.cln_y = [event.ydata, ]
            logger.debug("set cloning point: (%f, %f)" % (self.cln_x[0], self.cln_y[0]))

        self.cln_ax.set_offsets(np.vstack((self.cln_x, self.cln_y)).T)
        self.redraw()

    def on_pick(self, event) -> None:
        """Manage pick event"""
        # logger.debug("pick: %s" % event.artist)

        if event.mouseevent.button != 1:
            return

        artist = event.artist
        if not isinstance(artist, image.AxesImage):
            return

        last_x = event.mouseevent.xdata
        last_y = event.mouseevent.ydata
        logger.debug("ground coords -> x: %.3f, y: %.3f" % (last_x, last_y))  # click location

        if self.erase_tool.isVisible():

            erase_str = self.erase_tool.algo.currentText()
            if erase_str == "Plain":
                erase_type = EraseType.Plain
            elif erase_str == "Triangle":
                erase_type = EraseType.Triangle
            elif erase_str == "Bell":
                erase_type = EraseType.Bell
            elif erase_str == "Hill":
                erase_type = EraseType.Hill
            else:
                raise RuntimeError("Unknown filter: %s" % erase_str)

            other_layers = None
            if self.erase_tool.all_layers.isChecked():
                other_layers = self.other_raster_layers_for_current_key()

            self.current_layer().erase(pnt_x=last_x, pnt_y=last_y,
                                       sz=self.erase_tool.size.value(),
                                       use_radius=self.erase_tool.radius.isChecked(),
                                       erase_type=erase_type,
                                       other_layers=other_layers)

        elif self.modify_tool.isVisible():

            filter_str = self.modify_tool.algo.currentText()
            if filter_str == "Gaussian Filter":
                filter_type = FilterType.Gaussian
            elif filter_str == "Median Filter":
                filter_type = FilterType.Median
            else:
                raise RuntimeError("Unknown filter: %s" % filter_str)

            self.current_layer().modify(pnt_x=last_x, pnt_y=last_y,
                                        sz=self.modify_tool.size.value(),
                                        use_radius=self.modify_tool.radius.isChecked(),
                                        whole=self.modify_tool.whole.isChecked(),
                                        filter_type=filter_type,
                                        random_noise=self.modify_tool.noise.isChecked())

        elif self.clone_tool.isVisible():

            if len(self.cln_x) == 0:
                msg = "First middle click on the area to be used\n as a reference for the cloning."
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.information(self, "Cloning Info", msg, QtWidgets.QMessageBox.Ok)
                return

            filter_str = self.clone_tool.algo.currentText()
            if filter_str == "Bell":
                filter_type = CloneType.Bell
            elif filter_str == "Hill":
                filter_type = CloneType.Hill
            elif filter_str == "Triangle":
                filter_type = CloneType.Triangle
            elif filter_str == "Plain":
                filter_type = CloneType.Plain
            elif filter_str == "Averaged":
                filter_type = CloneType.Averaged
            elif filter_str == "Plain Noise":
                filter_type = CloneType.Noise
            elif filter_str == "Triangular Noise":
                filter_type = CloneType.TriangleNoise
            elif filter_str == "Bell-shaped Noise":
                filter_type = CloneType.BellNoise
            else:
                raise RuntimeError("Unknown filter: %s" % filter_str)

            self.current_layer().clone(pnt_x=last_x, pnt_y=last_y,
                                       clone_x=self.cln_x[0], clone_y=self.cln_y[0],
                                       sz=self.clone_tool.size.value(),
                                       use_radius=self.clone_tool.radius.isChecked(),
                                       filter_type=filter_type)

        else:  # nothing to do
            return

        self.update_plot_data()

    def on_enter_axes(self, event: QtGui.QMouseEvent) -> None:

        if self.prj.has_layers():
            logger.debug("entering axes")
            self.mouse_patch.set_visible(True)
            self.c.draw_idle()

    def on_leave_axes(self, event: QtGui.QMouseEvent) -> None:

        if self.prj.has_layers():
            logger.debug("leaving axes")
            self.mouse_patch.set_visible(False)
            self.c.draw_idle()

    # ### BUTTONS' ACTIONS ###

    def on_load_raster(self) -> None:
        logger.debug("User wants to load raster")

        self.main_win.switch_to_processing_tab()

        # noinspection PyCallByClass
        selection, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Add raster",
                                                             self.settings.value(app_info.key_raster_import_folder),
                                                             "Supported formats (*.asc; *.bag; *.tif; *.tiff);;"
                                                             "BAG format (*.bag);;"
                                                             "GeoTiff format (*.tif; *.tiff);;"
                                                             "ASCII grid format (*.asc)")
        if selection == str():
            logger.debug('adding raster: aborted')
            return

        last_open_folder = os.path.dirname(selection)
        if os.path.exists(last_open_folder):
            self.settings.setValue(app_info.key_raster_import_folder, last_open_folder)

        self.load_raster(path=selection)

    def on_info_raster(self) -> None:
        layer_key = self.current_layer_key()
        logger.debug("User wants to retrieve info from %s" % layer_key)

        msg = "Layer Key: %s\n\n%s" % (layer_key, self.prj.layers_dict[layer_key].info_str())
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Grid Info", msg, QtWidgets.QMessageBox.Ok)

    def on_data_spreadsheet(self) -> None:
        logger.debug("User wants to view raster data on a spreadsheet")
        d = ArrayExplorer(layer=self.current_layer(), parent=self,
                          with_menu=False, with_info_button=False, with_help_button=False)
        _ = d.exec_()

    def on_histo_raster(self) -> None:
        logger.debug("User wants to plot raster histogram")

        array = self.current_layer_array()

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
            plt.text(min_range + delta, 0.01, "%.2f" % min_range, color='r')

            plt.axvline(avg_value, color='y', linestyle=':', label="mean")
            plt.text(avg_value + delta, 0.01, "%.2f" % avg_value, color='y')

            plt.axvline(med_value, color='m', linestyle=':', label="median")
            plt.text(med_value + delta, 0.01, "%.2f" % med_value, color='m')

            plt.axvline(max_range, color='b', linestyle=':', label="max")
            plt.text(max_range + delta, 0.01, "%.2f" % max_range, color='b')

            plt.grid(True)
            plt.legend()
            plt.show()

        logger.debug("plotting raster histogram: done!")

    def on_save_raster(self) -> None:
        layer_key = self.current_layer_key()
        logger.debug("User wants to save the current raster [%s]" % layer_key)

        layer = self.prj.layers_dict[layer_key]
        title = "Save raster"
        ext = "All files (*.*)"
        if layer.format_type == FormatType.BAG:
            title = "Save BAG"
            ext = "BAG file (*.bag)"
        elif layer.format_type == FormatType.GEOTIFF:
            title = "Save GeoTiff"
            ext = "GeoTiff file (*.tif)"
        elif layer.format_type == FormatType.ASC_GRID:
            title = "Save ASCII Grid"
            ext = "ASCII Grid file (*.asc)"

        default_output = os.path.join(self.settings.value(app_info.key_raster_export_folder, self.prj.export_folder),
                                      layer_key.split(":")[-1])

        # noinspection PyCallByClass
        out_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, title, default_output, ext)
        if out_path == str():
            logger.debug('saving raster: aborted')
            return

        # checking filenaming convention
        is_checked = self.settings.value(app_info.key_output_filename_convention, "True") == "True"
        if is_checked:
            out_path_basename = os.path.basename(out_path)
            if "_sensitive" in out_path_basename.lower():
                msg = "The selected output filename '%s' has the '_SENSITIVE' substring.\n\n" \
                      "Do you still want to save the file?" % out_path_basename
                # noinspection PyCallByClass
                ret = QtWidgets.QMessageBox.warning(self, "File Naming", msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return

        last_open_folder = os.path.dirname(out_path)
        if os.path.exists(last_open_folder):
            QtCore.QSettings().setValue(app_info.key_raster_export_folder, last_open_folder)

        success = self.prj.save_layer_by_key(layer_key=layer_key, output_path=out_path, open_folder=True)

        if success:
            logger.debug("Saving done!")
        else:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Saving Error",
                                           "An issue occurred while saving %s" % layer_key,
                                           QtWidgets.QMessageBox.Ok)

    def on_open_output_folder(self):
        output_folder = self.settings.value(app_info.key_raster_export_folder, self.prj.export_folder)
        if not os.path.exists(output_folder):
            logger.warning("unable to locate output folder: %s" % output_folder)
            return
        Helper.explore_folder(path=output_folder)

    def on_show_settings(self):
        logger.debug("show settings")
        settings_dialog = SettingsDialog(parent=self)
        settings_dialog.exec_()

    def on_unload_raster(self):
        logger.debug("User wants to unload raster")
        self.prj.close_layer_by_basename(self.current_layer_key().split(":")[-1])
        self.update_layers_combo()

        # if there are not layers, we triggered raster_unloaded; otherwise, now we trigger the visualization
        if len(self.prj.layers_list) == 0:
            self._raster_unloaded()
            self.on_empty_draw()
            self.c.resize_event()
        else:
            self.layers_combo.setCurrentIndex(0)
            self.on_layers_combo(0)
        return True

    def _raster_loaded(self):

        self.info_act.setEnabled(True)
        self.spreadsheet_act.setEnabled(True)
        self.histo_act.setEnabled(True)
        self.save_act.setEnabled(True)
        self.unload_act.setEnabled(True)

        self.layers_combo.setEnabled(True)
        self.colors_act.setEnabled(True)
        self.shift_act.setEnabled(True)
        self.erase_act.setEnabled(True)
        self.modify_act.setEnabled(True)
        self.clone_act.setEnabled(True)

    def _raster_unloaded(self):

        self.info_act.setDisabled(True)
        self.spreadsheet_act.setDisabled(True)
        self.histo_act.setDisabled(True)
        self.save_act.setDisabled(True)
        self.unload_act.setDisabled(True)

        if len(self.prj.layers_list) == 0:
            self.layers_combo.setDisabled(True)
        self.colors_act.setDisabled(True)
        self.shift_act.setDisabled(True)
        self.erase_act.setDisabled(True)
        self.modify_act.setDisabled(True)
        self.clone_act.setDisabled(True)
        self.undo_act.setDisabled(True)

    def _vector_loaded(self):

        self.info_act.setEnabled(True)
        self.spreadsheet_act.setEnabled(False)  # nothing to spreadsheet
        self.histo_act.setEnabled(False)  # nothing to histogram
        self.save_act.setEnabled(True)
        self.unload_act.setEnabled(True)

        self.layers_combo.setEnabled(True)
        self.colors_act.setEnabled(False)
        self.shift_act.setEnabled(False)
        self.erase_act.setEnabled(True)
        self.modify_act.setEnabled(False)
        self.clone_act.setEnabled(False)

    def _vector_unloaded(self):

        self.info_act.setDisabled(True)
        self.spreadsheet_act.setDisabled(True)
        self.histo_act.setDisabled(True)
        self.save_act.setDisabled(True)
        self.unload_act.setDisabled(True)

        if len(self.prj.layers_list) == 0:
            self.layers_combo.setDisabled(True)
        self.colors_act.setDisabled(True)
        self.shift_act.setDisabled(True)
        self.erase_act.setDisabled(True)
        self.modify_act.setDisabled(True)
        self.clone_act.setDisabled(True)
        self.undo_act.setDisabled(True)

    # ### PROCESSING ###

    def load_raster(self, path: str):

        logger.debug("loading %s" % path)

        if self.prj.is_vr(path=path):
            msg = "The input file is at Variable Resolution.\n\n" \
                  "VR grids are currently unsupported!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Variable Resolution Grid", msg, QtWidgets.QMessageBox.Ok)
            return

        # we need to ask the user in case of ASCII Grid format
        hint_type = LayerType.UNKNOWN
        if os.path.splitext(path)[-1] in [".asc", ]:

            list_types = ["Bathymetry", "Uncertainty", "Mosaic"]
            # noinspection PyCallByClass
            type_str, ok = QtWidgets.QInputDialog.getItem(self, "ASCII Grid input", "Data type:", list_types, 0, False)
            if not ok:
                return LayerType.UNKNOWN

            if type_str == "Bathymetry":
                hint_type = LayerType.BATHYMETRY
            elif type_str == "Uncertainty":
                hint_type = LayerType.UNCERTAINTY
            elif type_str == "Mosaic":
                hint_type = LayerType.MOSAIC

        # store if the project had layers before adding
        had_layers = self.prj.has_layers()

        # Try to load the layers
        success = self.prj.load_from_source(path=path, hint_type=hint_type)
        if not success:
            msg = "Unable to load the selected file!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Raster Issue", msg, QtWidgets.QMessageBox.Ok)
            return

        if not had_layers:
            self.on_first_draw()

        self.update_layers_combo()
        self.layers_combo.setCurrentIndex(0)
        self.on_layers_combo(0)

    # ### LAYERS_COMBO ###

    def current_layer_key(self) -> str:
        return self.layers_combo.currentText()

    def other_raster_layers_for_current_key(self) -> list:
        return self.prj.other_raster_layers_for_key(layer_key=self.current_layer_key())

    def current_layer(self) -> Layer:
        return self.prj.layers_dict[self.current_layer_key()]

    def current_layer_array(self) -> np.ndarray:
        return self.current_layer().array

    def update_layers_combo(self):
        # noinspection PyUnresolvedReferences
        self.layers_combo.currentIndexChanged.disconnect()

        self.layers_combo.clear()

        for lk in self.prj.ordered_layers_list:

            self.layers_combo.addItem(lk)

        # noinspection PyUnresolvedReferences
        self.layers_combo.currentIndexChanged.connect(self.on_layers_combo)

    def on_layers_combo(self, index):
        layer_key = self.current_layer_key()
        logger.debug("combo index: [%d] %s" % (index, layer_key))
        layer = self.current_layer()

        if layer.is_raster():
            logger.debug("is raster")
            self.mat_ax.set_data(layer.array)
            self.mat_ax.set_extent(layer.plot.extent)
            self.mat_ax.set_clim(layer.plot.clim)
            self.mat_ax.set_cmap(layer.plot.cmap)
            if layer.plot.with_shading:
                self.shd_ax.set_data(layer.plot.shaded)
            else:
                self.shd_ax.set_data(self.nan_arr)
            self.shd_ax.set_extent(layer.plot.extent)

            if layer.undo_array_available():
                self.activate_undo()
            else:
                self.deactivate_undo()

            self.set_plot_aspect_and_positions()

            self._raster_loaded()

        else:
            self.mat_ax.set_data(self.nan_arr)
            self.shd_ax.set_data(self.nan_arr)

        if layer.is_vector():
            self.fts_ax.set_offsets(np.vstack((layer.features_x, layer.features_y)).T)

            self._vector_loaded()

        else:
            self.fts_ax.set_offsets(np.vstack(([], [])).T)

        self.c.resize_event()
        self.close_all_tools()

    # ### TOOLS ###

    def close_all_tools(self):
        self.colors_act.setChecked(False)
        self.shift_act.setChecked(False)
        self.erase_act.setChecked(False)
        self.modify_act.setChecked(False)
        self.clone_act.setChecked(False)

        self.close_colors_tool()
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.close_clone_tool()

    # colors

    def on_colors_tool(self):
        if self.colors_act.isChecked():
            self.open_colors_tool()

            self.shift_act.setChecked(False)
            self.erase_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.close_colors_tool()

    def open_colors_tool(self):
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.close_clone_tool()
        self.colors_tool.show()

    def close_colors_tool(self):
        self.colors_tool.hide()

    # shift

    def on_shift_tool(self):
        if self.shift_act.isChecked():
            self.open_shift_tool()

            self.colors_act.setChecked(False)
            self.erase_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.close_shift_tool()

    def open_shift_tool(self):
        self.close_colors_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.close_clone_tool()
        self.shift_tool.show()

    def close_shift_tool(self):
        self.shift_tool.hide()

    # erase

    def on_erase_tool(self):
        if self.erase_act.isChecked():
            self.open_erase_tool()

            self.colors_act.setChecked(False)
            self.shift_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.close_erase_tool()

    def open_erase_tool(self):
        self.close_colors_tool()
        self.close_shift_tool()
        self.close_modify_tool()
        self.close_clone_tool()
        self.erase_tool.show()

    def close_erase_tool(self):
        self.erase_tool.hide()

    # modify

    def on_modify_tool(self):
        if self.modify_act.isChecked():
            self.open_modify_tool()

            self.colors_act.setChecked(False)
            self.shift_act.setChecked(False)
            self.erase_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.close_modify_tool()

    def open_modify_tool(self):
        self.close_colors_tool()
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_clone_tool()
        self.modify_tool.show()

    def close_modify_tool(self):
        self.modify_tool.hide()

    # clone

    def on_clone_tool(self):
        if self.clone_act.isChecked():
            self.open_clone_tool()

            self.colors_act.setChecked(False)
            self.shift_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.erase_act.setChecked(False)
        else:
            self.close_clone_tool()

    def open_clone_tool(self):
        self.close_colors_tool()
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.clone_tool.show()

    def close_clone_tool(self):
        self.clone_tool.hide()

    # undo

    def on_undo(self):
        logger.debug("User wants to undo the latest change")

        layer = self.current_layer()
        if layer.is_raster():
            layer.undo_array()
        if layer.is_vector():
            layer.undo_features()

        self.update_plot_data()

    def activate_undo(self):
        self.undo_act.setEnabled(True)

    def deactivate_undo(self):
        self.undo_act.setDisabled(True)

    # # ### PLOTTING ###

    def set_plot_aspect_and_positions(self):
        self.data_ax.set_aspect(1.0)
        self.data_ax.set_position([0.06, 0.02, 0.85, 0.94])
        self.colorbar.ax.set_position([0.93, 0.02, 0.03, 0.94])

    def on_empty_draw(self):

        with rc_context(app_info.plot_rc_context):
            self.data_ax.clear()

            if self.colorbar:
                self.colorbar.remove()
                self.colorbar = None

            img = np.flipud(image.imread(os.path.join(app_info.app_media_path, "stencil.png")))
            self.data_ax.imshow(img, origin='lower')
            self.data_ax.axis('off')

            self.c.draw()

    def on_first_draw(self):

        origin = "lower"

        with rc_context(app_info.plot_rc_context):
            self.data_ax.clear()

            self.mat_ax = self.data_ax.matshow(self.nan_arr,
                                               extent=(0, 1, 0, 1),
                                               aspect='equal',
                                               origin=origin,
                                               interpolation='none',
                                               picker=True)

            self.colorbar = self.f.colorbar(self.mat_ax, shrink=.5)

            self.shd_ax = self.data_ax.matshow(self.nan_arr,
                                               extent=(0, 1, 0, 1),
                                               aspect='equal',
                                               origin=origin,
                                               interpolation='none',
                                               cmap=Plotting.shadow_cmap,
                                               vmin=0.0, vmax=1.0)

            self.cln_ax = self.data_ax.scatter(x=self.cln_x, y=self.cln_y,
                                               s=24, c=Plotting.magenta_color, marker="*", alpha=0.8)
            self.fts_ax = self.data_ax.scatter(x=[], y=[],
                                               s=24, c=Plotting.orange_color, marker="x", alpha=0.8)
            self.mouse_ax = self.data_ax.add_patch(self.mouse_patch)

            def format_coord(easting, northing):

                if self.prj.has_layers():

                    layer = self.current_layer()

                    col, row = layer.xy2cr(x=easting, y=northing)
                    if (col is None) or (row is None):
                        return "XY(%.2f, %.2f)" % (easting, northing)

                    if layer.is_raster():
                        if np.isnan(layer.array[row, col]):
                            return "XY(%.2f, %.2f)->(%d, %d)" \
                                    % (easting, northing, row, col)
                        else:
                            return "XY(%.2f, %.2f)->(%d, %d) %.2f" \
                                    % (easting, northing, row, col, layer.array[row, col])
                    if layer.is_vector():
                        feature = layer.feature_at_row_col(r=row, c=col)
                        if feature is None:
                            return "XY(%.2f, %.2f)->(%d, %d)" \
                                    % (easting, northing, row, col)
                        else:
                            return "XY(%.2f, %.2f)->(%d, %d) {orig. %.2f, %.2f}" \
                                    % (easting, northing, row, col, feature['depth'], feature['uncertainty'])

                return "XY(%.2f, %.2f)" % (easting, northing)

            self.data_ax.format_coord = format_coord
            self.data_ax.xaxis.set_ticks_position('bottom')

            self.data_ax.grid(True)
            self.set_plot_aspect_and_positions()

            self.c.draw()

    def redraw(self):
        """Redraw the canvases, update the locators"""

        with rc_context(app_info.plot_rc_context):
            for a in self.c.figure.get_axes():

                xaxis = getattr(a, 'xaxis', None)
                yaxis = getattr(a, 'yaxis', None)
                locators = []

                if xaxis is not None:
                    locators.append(xaxis.get_major_locator())
                    locators.append(xaxis.get_minor_locator())

                if yaxis is not None:
                    locators.append(yaxis.get_major_locator())
                    locators.append(yaxis.get_minor_locator())

                for loc in locators:
                    loc.refresh()

            self.c.draw_idle()

    def update_plot_data(self):
        layer_key = self.current_layer_key()
        logger.debug("update %s" % (layer_key, ))

        layer = self.current_layer()

        if layer.is_raster():
            self.mat_ax.set_data(layer.array)
            self.mat_ax.set_clim(layer.plot.clim)

            if layer.plot.with_shading:
                self.shd_ax.set_data(layer.plot.shaded)
            else:
                self.shd_ax.set_data(self.nan_arr)

            if layer.undo_array_available():
                self.activate_undo()
            else:
                self.deactivate_undo()

        if layer.is_vector():
            self.fts_ax.set_offsets(np.vstack((layer.features_x, layer.features_y)).T)

            if layer.undo_features_available():
                self.activate_undo()
            else:
                self.deactivate_undo()

        self.redraw()

    def update_shading(self):
        layer = self.current_layer()
        if layer.plot.with_shading:
            self.shd_ax.set_data(layer.plot.shaded)
        else:
            self.shd_ax.set_data(self.nan_arr)

        self.redraw()

    def update_plot_cmap(self):
        self.mat_ax.set_cmap(self.current_layer().plot.cmap)
        self.redraw()

    def update_plot_range(self):
        self.mat_ax.set_clim(self.current_layer().plot.clim)
        self.redraw()
