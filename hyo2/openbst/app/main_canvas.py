import logging
import os
from PySide2 import QtCore, QtGui, QtWidgets
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import patches
from matplotlib import rc_context
from matplotlib import image

from hyo2.openbst.app import app_info
from hyo2.openbst.app.bars.navigation_toolbar import NavToolbar
from hyo2.openbst.lib.sources.layer import EraseType, FilterType, CloneType
from hyo2.openbst.lib.plotting import Plotting

logger = logging.getLogger(__name__)


class MainCanvas(QtWidgets.QFrame):

    def __init__(self, main_win, main_tab, prj):
        super().__init__(parent=main_tab)
        self.main_win = main_win
        self.main_tab = main_tab
        self.prj = prj
        self.settings = QtCore.QSettings()

        # empty arrays
        self.nan_arr = np.zeros((1, 1), dtype=np.float32)
        self.nan_arr[:] = np.nan

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

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.plot_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.plot_layout)

        with rc_context(app_info.plot_rc_context):
            self.f = Figure()
            self.f.patch.set_alpha(0.0)
            self.c = FigureCanvas(self.f)
            self.c.setParent(self)
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
        self.nav = NavToolbar(canvas=self.c, parent=self)
        self.layout.addWidget(self.nav)

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
        if self.main_tab.product_erase_tool.isVisible():
            visible = True
            radius = self.main_tab.product_erase_tool.size.value()
        elif self.main_tab.product_modify_tool.isVisible():
            visible = True
            radius = self.main_tab.product_modify_tool.size.value()
        elif self.main_tab.product_clone_tool.isVisible():
            visible = True
            radius = self.main_tab.product_clone_tool.size.value()

        if visible:
            # logger.debug("visible")
            if (event.xdata is not None) and (event.ydata is not None):
                layer = self.main_tab.current_layer()
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

        if self.main_tab.product_erase_tool.isVisible():

            erase_str = self.main_tab.product_erase_tool.algo.currentText()
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
            if self.main_tab.product_erase_tool.all_layers.isChecked():
                other_layers = self.other_raster_layers_for_current_key()

            self.main_tab.current_layer().erase(pnt_x=last_x, pnt_y=last_y,
                                                sz=self.main_tab.product_erase_tool.size.value(),
                                                use_radius=self.main_tab.product_erase_tool.radius.isChecked(),
                                                erase_type=erase_type,
                                                other_layers=other_layers)

        elif self.main_tab.product_modify_tool.isVisible():

            filter_str = self.main_tab.product_modify_tool.algo.currentText()
            if filter_str == "Gaussian Filter":
                filter_type = FilterType.Gaussian
            elif filter_str == "Median Filter":
                filter_type = FilterType.Median
            else:
                raise RuntimeError("Unknown filter: %s" % filter_str)

            self.main_tab.current_layer().modify(pnt_x=last_x, pnt_y=last_y,
                                                 sz=self.main_tab.product_modify_tool.size.value(),
                                                 use_radius=self.main_tab.product_modify_tool.radius.isChecked(),
                                                 whole=self.main_tab.product_modify_tool.whole.isChecked(),
                                                 filter_type=filter_type,
                                                 random_noise=self.main_tab.product_modify_tool.noise.isChecked())

        elif self.main_tab.product_clone_tool.isVisible():

            if len(self.cln_x) == 0:
                msg = "First middle click on the area to be used\n as a reference for the cloning."
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.information(self, "Cloning Info", msg, QtWidgets.QMessageBox.Ok)
                return

            filter_str = self.main_tab.product_clone_tool.algo.currentText()
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

            self.main_tab.current_layer().clone(pnt_x=last_x, pnt_y=last_y,
                                                clone_x=self.cln_x[0], clone_y=self.cln_y[0],
                                                sz=self.main_tab.product_clone_tool.size.value(),
                                                use_radius=self.main_tab.product_clone_tool.radius.isChecked(),
                                                filter_type=filter_type)

        else:  # nothing to do
            return

        self.update_plot_data()

    def on_enter_axes(self, event: QtGui.QMouseEvent) -> None:

        if self.prj.has_layers():
            logger.debug("entering axes")
            self.mouse_patch.set_visible(True)
            event.canvas.draw_idle()

    def on_leave_axes(self, event: QtGui.QMouseEvent) -> None:

        if self.prj.has_layers():
            logger.debug("leaving axes")
            self.mouse_patch.set_visible(False)
            event.canvas.draw_idle()

    # # ### PLOTTING ###

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

                    layer = self.main_tab.file_products_bar.current_layer()

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

    def set_plot_aspect_and_positions(self):
        self.data_ax.set_aspect(1.0)
        self.data_ax.set_position([0.06, 0.02, 0.85, 0.94])
        self.colorbar.ax.set_position([0.93, 0.02, 0.03, 0.94])

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

    def change_layer(self, layer):

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

            self.set_plot_aspect_and_positions()

        else:
            self.mat_ax.set_data(self.nan_arr)
            self.shd_ax.set_data(self.nan_arr)

        if layer.is_vector():
            self.fts_ax.set_offsets(np.vstack((layer.features_x, layer.features_y)).T)

        else:
            self.fts_ax.set_offsets(np.vstack(([], [])).T)

        self.c.resize_event()

    def update_plot_data(self):
        layer_key = self.main_tab.current_layer_key()
        logger.debug("update %s" % (layer_key, ))

        layer = self.main_tab.current_layer()

        if layer.is_raster():
            self.mat_ax.set_data(layer.array)
            self.mat_ax.set_clim(layer.plot.clim)

            if layer.plot.with_shading:
                self.shd_ax.set_data(layer.plot.shaded)
            else:
                self.shd_ax.set_data(self.nan_arr)

            if layer.undo_array_available():
                self.main_tab.activate_undo()
            else:
                self.main_tab.deactivate_undo()

        if layer.is_vector():
            self.fts_ax.set_offsets(np.vstack((layer.features_x, layer.features_y)).T)

            if layer.undo_features_available():
                self.main_tab.activate_undo()
            else:
                self.main_tab.deactivate_undo()

        self.redraw()

    def update_shading(self):
        layer = self.main_tab.current_layer()
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

    def resize_event(self):
        self.c.resize_event()
