import logging
import os

import numpy as np
from PySide2 import QtCore, QtWidgets
import matplotlib

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.openbst.app.main_canvas import MainCanvas
from hyo2.openbst.app.bars.file_project_bar import FileProjectBar
from hyo2.openbst.app.bars.file_products_bar import FileProductsBar
from hyo2.openbst.app.bars.view_products_bar import ViewProductsBar
from hyo2.openbst.app.bars.edit_products_bar import EditProductsBar
from hyo2.openbst.app.bars.app_settings_bar import AppSettingsBar
from hyo2.openbst.app.tools.product_shift_tool import ProductShiftTool
from hyo2.openbst.app.tools.product_colors_tool import ProductColorsTool
from hyo2.openbst.app.tools.product_erase_tool import ProductEraseTool
from hyo2.openbst.app.tools.product_modify_tool import ProductModifyTool
from hyo2.openbst.app.tools.product_clone_tool import ProductCloneTool
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.products.product_layer import ProductLayer

matplotlib.use('Qt5Agg')
matplotlib.rcParams['axes.formatter.useoffset'] = False
logger = logging.getLogger(__name__)


class MainTab(QtWidgets.QMainWindow):

    def __init__(self, main_win):
        super().__init__(parent=main_win)
        self.setWindowTitle("Main Tab")
        self.settings = QtCore.QSettings()

        self.main_win = main_win
        self.lib = OpenBST(progress=QtProgress(self))
        self.tab_idx = -1
        self.progress = QtProgress(parent=self)

        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        self.setContentsMargins(0, 0, 0, 0)

        # ### CANVAS ###
        self.canvas = MainCanvas(main_win=self.main_win, main_tab=self, lib=self.lib)
        self.setCentralWidget(self.canvas)

        # ### FILE PROJECT BAR ###
        self.file_project_bar = FileProjectBar(main_win=self.main_win, main_tab=self,
                                               canvas=self.canvas, lib=self.lib)
        # noinspection PyArgumentList
        self.addToolBar(self.file_project_bar)

        # ### FILE PRODUCTS BAR ###
        self.file_products_bar = FileProductsBar(main_win=self.main_win, main_tab=self,
                                                 canvas=self.canvas, lib=self.lib)
        # noinspection PyArgumentList
        self.addToolBar(self.file_products_bar)

        # ### VIEW PRODUCTS TOOLBAR ###
        self.view_products_bar = ViewProductsBar(main_win=self.main_win, main_tab=self,
                                                 canvas=self.canvas, lib=self.lib)
        # noinspection PyArgumentList
        self.addToolBar(self.view_products_bar)

        # ### EDIT PRODUCTS TOOLBAR ###
        self.edit_products_bar = EditProductsBar(main_win=self.main_win, main_tab=self,
                                                 canvas=self.canvas, lib=self.lib)
        # noinspection PyArgumentList
        self.addToolBar(self.edit_products_bar)

        # ### APP SETTINGS BAR ###
        self.app_settings_bar = AppSettingsBar(main_win=self.main_win, main_tab=self,
                                               canvas=self.canvas, lib=self.lib)
        # noinspection PyArgumentList
        self.addToolBar(self.app_settings_bar)

        # ### TOOLS ###
        self.product_colors_tool = ProductColorsTool(main_win=self.main_win, main_tab=self,
                                                     main_canvas=self.canvas, lib=self.lib)
        self.product_shift_tool = ProductShiftTool(main_win=self.main_win, main_tab=self,
                                                   main_canvas=self.canvas, lib=self.lib)
        self.product_erase_tool = ProductEraseTool(main_win=self.main_win, main_tab=self,
                                                   main_canvas=self.canvas, lib=self.lib)
        self.product_modify_tool = ProductModifyTool(main_win=self.main_win, main_tab=self,
                                                     main_canvas=self.canvas, lib=self.lib)
        self.product_clone_tool = ProductCloneTool(main_win=self.main_win, main_tab=self,
                                                   main_canvas=self.canvas, lib=self.lib)

        self.on_empty_draw()

    # ### ICON SIZE ###

    def toolbars_icon_size(self) -> int:
        return self.file_products_bar.iconSize().height()

    def set_toolbars_icon_size(self, icon_size: int) -> None:
        self.file_products_bar.setIconSize(QtCore.QSize(icon_size, icon_size))

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
                    # noinspection PyCallByClass,PyArgumentList
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
                    # noinspection PyCallByClass,PyArgumentList
                    QtWidgets.QMessageBox.critical(self, "Input Error", msg, QtWidgets.QMessageBox.Ok)

        else:
            e.ignore()

    def change_layer(self, layer):

        self.canvas.change_layer(layer=layer)

        if layer.is_raster():
            logger.debug("is raster")
            if layer.undo_array_available():
                self.activate_undo()
            else:
                self.deactivate_undo()
            self.raster_loaded()

        if layer.is_vector():
            self.vector_loaded()

        self.close_all_tools()

    # ### BUTTONS' ACTIONS ###

    def raster_loaded(self):
        self.file_products_bar.raster_loaded()
        self.view_products_bar.raster_loaded()
        self.edit_products_bar.raster_loaded()

    def raster_unloaded(self):
        self.file_products_bar.raster_unloaded()
        self.view_products_bar.raster_unloaded()
        self.edit_products_bar.raster_unloaded()

    def vector_loaded(self):
        self.file_products_bar.vector_loaded()
        self.view_products_bar.vector_loaded()
        self.edit_products_bar.vector_loaded()

    def vector_unloaded(self):
        self.file_products_bar.vector_unloaded()
        self.view_products_bar.vector_unloaded()
        self.edit_products_bar.vector_unloaded()

    # ### TOOLS ###

    def close_all_tools(self):
        self.edit_products_bar.uncheck_all_tools()

        self.close_colors_tool()
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.close_clone_tool()

    # colors

    def open_colors_tool(self):
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.close_clone_tool()
        self.product_colors_tool.show()

    def close_colors_tool(self):
        self.product_colors_tool.hide()

    # shift

    def open_shift_tool(self):
        self.close_colors_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.close_clone_tool()
        self.product_shift_tool.show()

    def close_shift_tool(self):
        self.product_shift_tool.hide()

    # erase

    def open_erase_tool(self):
        self.close_colors_tool()
        self.close_shift_tool()
        self.close_modify_tool()
        self.close_clone_tool()
        self.product_erase_tool.show()

    def close_erase_tool(self):
        self.product_erase_tool.hide()

    # modify

    def open_modify_tool(self):
        self.close_colors_tool()
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_clone_tool()
        self.product_modify_tool.show()

    def close_modify_tool(self):
        self.product_modify_tool.hide()

    # clone

    def open_clone_tool(self):
        self.close_colors_tool()
        self.close_shift_tool()
        self.close_erase_tool()
        self.close_modify_tool()
        self.product_clone_tool.show()

    def close_clone_tool(self):
        self.product_clone_tool.hide()

    # undo

    def activate_undo(self):
        self.edit_products_bar.activate_undo()

    def deactivate_undo(self):
        self.edit_products_bar.deactivate_undo()

    # # ### PLOTTING ###

    def on_empty_draw(self):
        self.canvas.on_empty_draw()

    def on_first_draw(self):
        self.canvas.on_first_draw()

    def redraw(self):
        self.canvas.redraw()

    def update_plot_data(self):
        self.canvas.update_plot_data()

    def update_shading(self):
        self.canvas.update_shading()

    def update_plot_cmap(self):
        self.canvas.update_plot_cmap()

    def update_plot_range(self):
        self.canvas.update_plot_range()

    def current_layer_key(self) -> str:
        return self.file_products_bar.current_layer_key()

    def current_layer(self) -> ProductLayer:
        return self.file_products_bar.current_layer()

    def current_layer_array(self) -> np.ndarray:
        return self.file_products_bar.current_layer_array()
