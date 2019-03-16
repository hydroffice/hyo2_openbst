import logging
import os
import numpy as np
from PySide2 import QtGui, QtWidgets

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.lib.sources.layer_type import LayerType
from hyo2.openbst.lib.sources.format import FormatType
from hyo2.openbst.lib.sources.layer import Layer
from hyo2.openbst.app import app_info
from hyo2.openbst.app.bars.abstract_bar import AbstractBar

logger = logging.getLogger(__name__)


class FileProductsBar(AbstractBar):

    def __init__(self, main_win, main_tab, canvas, prj):
        super().__init__(main_tab=main_tab, main_win=main_win, canvas=canvas, prj=prj)
        self.setWindowTitle("File Raster/Vector")

        self.setMinimumWidth(480)

        # load raster
        tip = 'Load raster/vector'
        self.load_product_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'add_grid.png')),
                                                  tip, self)
        # noinspection PyTypeChecker
        self.load_product_act.setShortcut('Alt+L')
        self.load_product_act.setStatusTip(tip)
        # noinspection PyUnresolvedReferences
        self.load_product_act.triggered.connect(self.on_load_product)
        self.addAction(self.load_product_act)
        self.main_win.menu_file_products.addAction(self.load_product_act)

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
        self.addWidget(self.layers_combo)

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
        self.addAction(self.unload_act)
        self.main_win.menu_file_products.addAction(self.unload_act)

        self.addSeparator()

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
        self.addAction(self.save_act)
        self.main_win.menu_file_products.addAction(self.save_act)

        # output
        tip = 'Open output folder'
        self.open_output_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'open_output.png')),
                                                 tip, self)
        self.open_output_act.setStatusTip(tip)
        # self.open_output_act.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.open_output_act.triggered.connect(self.on_open_output_folder)
        self.addAction(self.open_output_act)
        self.main_win.menu_file_products.addAction(self.open_output_act)

    def on_load_product(self) -> None:
        logger.debug("User wants to load raster")

        self.main_win.switch_to_main_tab()

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

    def on_layers_combo(self, index):
        layer_key = self.current_layer_key()
        logger.debug("combo index: [%d] %s" % (index, layer_key))
        layer = self.current_layer()
        self.main_tab.change_layer(layer)

    def on_unload_raster(self):
        logger.debug("User wants to unload raster")
        self.prj.close_layer_by_basename(self.current_layer_key().split(":")[-1])
        self.update_layers_combo()

        # if there are not layers, we triggered raster_unloaded; otherwise, now we trigger the visualization
        if len(self.prj.layers_list) == 0:
            self.main_tab.raster_unloaded()
            self.main_tab.on_empty_draw()
            self.canvas.resize_event()
        else:
            self.layers_combo.setCurrentIndex(0)
            self.on_layers_combo(0)
        return True

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

        last_open_folder = os.path.dirname(out_path)
        if os.path.exists(last_open_folder):
            self.settings.setValue(app_info.key_raster_export_folder, last_open_folder)

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

    # ### LAYERS_COMBO ###

    def current_layer_key(self) -> str:
        return self.layers_combo.currentText()

    def other_raster_layers_for_current_key(self) -> list:
        return self.prj.other_raster_layers_for_key(layer_key=self.current_layer_key())

    def current_layer(self) -> Layer:
        return self.prj.layers_dict[self.current_layer_key()]

    def current_layer_array(self) -> np.ndarray:
        return self.current_layer().array

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
            self.main_tab.on_first_draw()

        self.update_layers_combo()
        self.layers_combo.setCurrentIndex(0)
        self.on_layers_combo(0)

    def update_layers_combo(self):
        # noinspection PyUnresolvedReferences
        self.layers_combo.currentIndexChanged.disconnect()

        self.layers_combo.clear()

        for lk in self.prj.ordered_layers_list:

            self.layers_combo.addItem(lk)

        # noinspection PyUnresolvedReferences
        self.layers_combo.currentIndexChanged.connect(self.on_layers_combo)

    def raster_loaded(self):
        self.layers_combo.setEnabled(True)
        self.save_act.setEnabled(True)
        self.unload_act.setEnabled(True)

    def raster_unloaded(self):
        if len(self.prj.layers_list) == 0:
            self.layers_combo.setDisabled(True)
        self.save_act.setDisabled(True)
        self.unload_act.setDisabled(True)

    def vector_loaded(self):
        self.layers_combo.setEnabled(True)
        self.save_act.setEnabled(True)
        self.unload_act.setEnabled(True)

    def vector_unloaded(self):
        if len(self.prj.layers_list) == 0:
            self.layers_combo.setDisabled(True)
        self.save_act.setDisabled(True)
        self.unload_act.setDisabled(True)
