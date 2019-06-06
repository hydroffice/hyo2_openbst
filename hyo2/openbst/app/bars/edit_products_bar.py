import logging
import os

from hyo2.openbst.app import app_info
from hyo2.openbst.app.bars.abstract_bar import AbstractBar

from PySide2 import QtGui, QtWidgets

logger = logging.getLogger(__name__)


class EditProductsBar(AbstractBar):

    def __init__(self, main_win, main_tab, canvas, lib):
        super().__init__(main_tab=main_tab, main_win=main_win, canvas=canvas, lib=lib)
        self.setWindowTitle("Edit Raster/Vector")

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
        self.addAction(self.colors_act)
        self.main_win.menu_edit_products.addAction(self.colors_act)

        self.addSeparator()

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
        self.addAction(self.shift_act)
        self.main_win.menu_edit_products.addAction(self.shift_act)

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
        self.addAction(self.erase_act)
        self.main_win.menu_edit_products.addAction(self.erase_act)

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
        self.addAction(self.modify_act)
        self.main_win.menu_edit_products.addAction(self.modify_act)

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
        self.addAction(self.clone_act)
        self.main_win.menu_edit_products.addAction(self.clone_act)

        self.addSeparator()

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
        self.addAction(self.undo_act)
        self.main_win.menu_edit_products.addAction(self.undo_act)

    def on_colors_tool(self):
        if self.colors_act.isChecked():
            self.main_tab.open_colors_tool()

            self.shift_act.setChecked(False)
            self.erase_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.main_tab.close_colors_tool()

    def on_shift_tool(self):
        if self.shift_act.isChecked():
            self.main_tab.open_shift_tool()

            self.colors_act.setChecked(False)
            self.erase_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.main_tab.close_shift_tool()

    def on_erase_tool(self):
        if self.erase_act.isChecked():
            self.main_tab.open_erase_tool()

            self.colors_act.setChecked(False)
            self.shift_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.main_tab.close_erase_tool()

    def on_modify_tool(self):
        if self.modify_act.isChecked():
            self.main_tab.open_modify_tool()

            self.colors_act.setChecked(False)
            self.shift_act.setChecked(False)
            self.erase_act.setChecked(False)
            self.clone_act.setChecked(False)
        else:
            self.main_tab.close_modify_tool()

    def on_clone_tool(self):
        if self.clone_act.isChecked():
            self.main_tab.open_clone_tool()

            self.colors_act.setChecked(False)
            self.shift_act.setChecked(False)
            self.modify_act.setChecked(False)
            self.erase_act.setChecked(False)
        else:
            self.main_tab.close_clone_tool()

    def on_undo(self):
        logger.debug("User wants to undo the latest change")

        layer = self.main_tab.current_layer()
        if layer.is_raster():
            layer.undo_array()
        if layer.is_vector():
            layer.undo_features()

        self.main_tab.update_plot_data()

    def activate_undo(self):
        self.undo_act.setEnabled(True)

    def deactivate_undo(self):
        self.undo_act.setDisabled(True)

    def uncheck_all_tools(self):
        self.colors_act.setChecked(False)
        self.shift_act.setChecked(False)
        self.erase_act.setChecked(False)
        self.modify_act.setChecked(False)
        self.clone_act.setChecked(False)

    def raster_loaded(self):
        self.colors_act.setEnabled(True)
        self.shift_act.setEnabled(True)
        self.erase_act.setEnabled(True)
        self.modify_act.setEnabled(True)
        self.clone_act.setEnabled(True)

    def raster_unloaded(self):
        self.colors_act.setDisabled(True)
        self.shift_act.setDisabled(True)
        self.erase_act.setDisabled(True)
        self.modify_act.setDisabled(True)
        self.clone_act.setDisabled(True)
        self.undo_act.setDisabled(True)

    def vector_loaded(self):
        self.colors_act.setEnabled(False)
        self.shift_act.setEnabled(False)
        self.erase_act.setEnabled(True)
        self.modify_act.setEnabled(False)
        self.clone_act.setEnabled(False)

    def vector_unloaded(self):
        self.colors_act.setDisabled(True)
        self.shift_act.setDisabled(True)
        self.erase_act.setDisabled(True)
        self.modify_act.setDisabled(True)
        self.clone_act.setDisabled(True)
        self.undo_act.setDisabled(True)
