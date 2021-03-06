import logging
import os
import socket
import ssl
import sys
import traceback
from urllib.request import urlopen, Request
from urllib.error import URLError
from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.app.dialogs.exception.exception_dialog import ExceptionDialog
from hyo2.abc.app.tabs.info.info_tab import InfoTab
from hyo2.openbst.lib import lib_info
from hyo2.openbst.app.arch import app_info
from hyo2.openbst.app.arch.arch_tab import ArchTab
from hyo2.openbst.app.arch.arch_tab_compare import ArchTabCompare
from hyo2.openbst.app.arch.arch_tab_3d import ArchTab3D

logger = logging.getLogger(__name__)


class ArchWindow(QtWidgets.QMainWindow):

    is_beta = True

    def __init__(self, parent=None, standalone=False):
        super().__init__(parent)
        self.standalone = standalone
        self.ask_quit = True
        self.settings = QtCore.QSettings()
        self.setObjectName(app_info.app_main_window_object_name)

        # set the application name and icon
        title = '%s v.%s' % (app_info.app_name, app_info.app_version)
        if self.is_beta:
            title += " BETA"
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(app_info.app_icon_path))

        # set the size
        self.setMinimumSize(QtCore.QSize(300, 200))
        self.resize(QtCore.QSize(800, 600))
        self.setContentsMargins(0, 0, 0, 0)

        # set status bar
        self.statusBar()
        self.status_bar_normal_style = self.statusBar().styleSheet()
        self.statusBar().showMessage("%s" % app_info.app_version, 2000)

        # create menu
        self.menu_root = self.menuBar()
        if self.standalone:
            self.menu_file = self.menu_root.addMenu("File")
        self.menu_setup = self.menu_root.addMenu("Setup")
        self.menu_help = self.menu_root.addMenu("Help")
        self.menu_setup_layout = None

        # add main frame and layout
        self.frame = QtWidgets.QFrame(parent=self)
        self.setCentralWidget(self.frame)
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.frame_layout)

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        # tabs icon sizes
        self.set_tabs_icon_size(int(self.settings.value("tabs/icon_size", app_info.app_tabs_icon_size)))
        # - Arch
        self.tab_arch = ArchTab(main_win=self)
        # noinspection PyArgumentList
        self.tab_arch_idx = self.tabs.insertTab(0, self.tab_arch,
                                                QtGui.QIcon(os.path.join(app_info.app_media_path, "tab_arch.png")),
                                                "")
        self.tabs.setTabToolTip(self.tab_arch_idx, "Arch")
        # - Arch Compare
        self.tab_compare = ArchTabCompare(main_win=self)
        # noinspection PyArgumentList
        self.tab_compare_idx = self.tabs.insertTab(1, self.tab_compare,
                                                   QtGui.QIcon(os.path.join(app_info.app_media_path,
                                                                            "tab_arch_compare.png")), "")
        self.tabs.setTabToolTip(self.tab_compare_idx, "Arch Compare")
        # - Arch 3D
        self.tab_arch3d = ArchTab3D(main_win=self)
        # noinspection PyArgumentList
        self.tab_arch3d_idx = self.tabs.insertTab(2, self.tab_arch3d,
                                                  QtGui.QIcon(os.path.join(app_info.app_media_path, "tab_arch_3d.png")),
                                                  "")
        self.tabs.setTabToolTip(self.tab_arch3d_idx, "Arch 3D")
        # - info
        if self.standalone:
            self.tab_info = InfoTab(main_win=self, lib_info=lib_info, app_info=app_info,
                                    with_online_manual=True,
                                    with_offline_manual=True,
                                    with_bug_report=True,
                                    with_hydroffice_link=True,
                                    with_ccom_link=True,
                                    with_noaa_link=True,
                                    with_unh_link=True,
                                    with_license=True)
            # noinspection PyArgumentList
            self.tab_info_idx = self.tabs.insertTab(3, self.tab_info,
                                                    QtGui.QIcon(os.path.join(app_info.app_media_path, "tab_info.png")),
                                                    "")
            self.tabs.setTabToolTip(self.tab_info_idx, "Info")
        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self._on_tab_changed)
        # add tabs
        self.frame_layout.addWidget(self.tabs)

        # toolbars icon sizes
        self.set_toolbars_icon_size(int(self.settings.value("toolbars/icon_size", app_info.app_toolbars_icon_size)))

        # finalize menus
        self.add_menus()

        # save default state and restore last state
        self.settings.setValue("main_window/geometry_default", self.saveGeometry())
        self.settings.setValue("main_window/state_default", self.saveState())
        self.restoreGeometry(self.settings.value("main_window/geometry"))
        self.restoreState(self.settings.value("main_window/state"))

        # periodical checks
        timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self.update_status)
        # noinspection PyArgumentList
        timer.start(300000)  # each 5 minutes
        self.update_status()

    def add_menus(self):

        # File

        if self.standalone:
            quit_icon = QtGui.QIcon(os.path.join(app_info.app_media_path, 'quit.png'))
            quit_act = QtWidgets.QAction(quit_icon, 'Exit', self)
            quit_act.setStatusTip('Close the application')
            # noinspection PyUnresolvedReferences
            quit_act.triggered.connect(self.close)
            self.menu_file.addAction(quit_act)

        # Setup

        self.menu_setup_layout = self.menu_setup.addMenu("Layout")

        reset_layout = QtWidgets.QAction('Reset layout', self)
        reset_layout.setStatusTip('Reset toolbars and menu')
        # noinspection PyUnresolvedReferences
        reset_layout.triggered.connect(self.reset_layout)
        self.menu_setup_layout.addAction(reset_layout)

        resize_tabs_icons = QtWidgets.QAction('Tabs icon size', self)
        resize_tabs_icons.setStatusTip('Resize the tabs icons')
        # noinspection PyUnresolvedReferences
        resize_tabs_icons.triggered.connect(self.resize_tabs_icons)
        self.menu_setup_layout.addAction(resize_tabs_icons)

        resize_toolbars_icons = QtWidgets.QAction('Toolbars icon size', self)
        resize_toolbars_icons.setStatusTip('Resize the toolbars icons')
        # noinspection PyUnresolvedReferences
        resize_toolbars_icons.triggered.connect(self.resize_toolbars_icons)
        self.menu_setup_layout.addAction(resize_toolbars_icons)

        # Help
        self.menu_help.addAction(self.tab_info.open_online_manual_action)
        self.menu_help.addAction(self.tab_info.open_offline_manual_action)
        self.menu_help.addAction(self.tab_info.fill_bug_report_action)
        self.menu_help.addAction(self.tab_info.authors_action)
        self.menu_help.addAction(self.tab_info.show_about_action)

    # ### APP APPEARANCE ###

    def reset_layout(self) -> None:
        logger.debug("reset layout")

        self.restoreState(self.settings.value("main_window/state_default"))
        self.restoreGeometry(self.settings.value("main_window/geometry_default"))
        self.set_tabs_icon_size(app_info.app_tabs_icon_size)
        self.set_toolbars_icon_size(app_info.app_toolbars_icon_size)

    def resize_tabs_icons(self) -> None:
        logger.debug("resize tabs icons")
        cur_size = int(self.tabs.iconSize().width())
        # noinspection PyCallByClass
        new_size, ret = QtWidgets.QInputDialog.getInt(
            self, "Tabs", "Set tabs icon size in pixels:", cur_size, 8, 126)
        if not ret:
            return
        self.set_tabs_icon_size(new_size)

    def set_tabs_icon_size(self, icon_size: int) -> None:
        self.tabs.setIconSize(QtCore.QSize(icon_size, icon_size))

    def resize_toolbars_icons(self) -> None:
        logger.debug("resize tabs icons")
        cur_size = self.tab_arch.toolbars_icon_size()
        # noinspection PyCallByClass
        new_size, ret = QtWidgets.QInputDialog.getInt(
            self, "Toolbars", "Set toolbars icon size in pixels:", cur_size, 8, 126)
        if not ret:
            return
        self.set_toolbars_icon_size(new_size)

    def set_toolbars_icon_size(self, icon_size: int) -> None:
        self.tab_arch.set_toolbars_icon_size(icon_size)
        if self.standalone:
            self.tab_info.set_toolbars_icon_size(icon_size)

    # ### TAB SWITCHERS ###

    def _on_tab_changed(self, idx) -> None:
        logger.debug("switch to tab #%d" % idx)
        if hasattr(self.tabs.currentWidget(), "redraw"):
            self.tabs.currentWidget().redraw()

    def switch_to_arch_tab(self) -> None:
        if self.tabs.currentIndex() != self.tab_arch_idx:
            self.tabs.setCurrentIndex(self.tab_arch_idx)

    def switch_to_compare_tab(self) -> None:
        if self.tabs.currentIndex() != self.tab_compare_idx:
            self.tabs.setCurrentIndex(self.tab_compare_idx)

    def switch_to_arch3d_tab(self) -> None:
        if self.tabs.currentIndex() != self.tab_arch3d_idx:
            self.tabs.setCurrentIndex(self.tab_arch3d_idx)

    def switch_to_info_tab(self) -> None:
        if self.tabs.currentIndex() != self.tab_info_idx:
            self.tabs.setCurrentIndex(self.tab_info_idx)

    def update_status(self) -> None:
        if not self.standalone:
            return
        msg = str()
        tokens = list()

        new_release = False
        new_bugfix = False
        latest_version = None
        try:
            req = Request(app_info.app_latest_url)
            with urlopen(req, timeout=1) as response:
                latest_version = response.read().split()[0].decode()

                cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
                lat_maj, lat_min, lat_fix = latest_version.split('.')

                if int(lat_maj) > int(cur_maj):
                    new_release = True

                elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                    new_release = True

                elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) \
                        and (int(lat_fix) > int(cur_fix)):
                    new_bugfix = True

        except (URLError, ssl.SSLError, socket.timeout) as e:
            logger.info("unable to check latest release: %s" % e)

        except ValueError as e:
            logger.info("unable to parse version: %s" % e)

        if new_release:
            logger.info("new release available: %s" % latest_version)
            tokens.append("New release available: %s" % latest_version)
            self.statusBar().setStyleSheet("QStatusBar{background-color:rgba(255,0,0,128);}")

        elif new_bugfix:
            logger.info("new bugfix available: %s" % latest_version)
            tokens.append("New bugfix available: %s" % latest_version)
            self.statusBar().setStyleSheet("QStatusBar{background-color:rgba(255,255,0,128);}")

        else:
            self.statusBar().setStyleSheet(self.status_bar_normal_style)

        msg += "|".join(tokens)

        self.statusBar().showMessage(msg, 3000000)

    def exception_hook(self, ex_type: type, ex_value: BaseException, tb: traceback) -> None:
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an exception (e.g., keyboard interrupts)
        if not issubclass(ex_type, Exception):
            msg = str(ex_value)
            if not msg:
                msg = ex_value.__class__.__name__
            logger.info(msg)
            self.close()
            return

        dlg = ExceptionDialog(app_info=app_info, lib_info=lib_info, ex_type=ex_type, ex_value=ex_value, tb=tb)
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Rejected:
            if not dlg.user_triggered:
                self.close()
        else:
            logger.warning("ignored exception")

    # Quitting #

    def do_you_really_want(self, title: str = "Quit", text: str = "quit") -> QtWidgets.QMessageBox.StandardButton:
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event: QtCore.QEvent) -> None:
        """ actions to be done before close the app """

        reply = QtWidgets.QMessageBox.Yes
        if self.ask_quit:
            reply = self.do_you_really_want(text="quit")

        if reply == QtWidgets.QMessageBox.Yes:

            # store current tab
            self.settings.setValue("tabs/icon_size", int(self.tabs.iconSize().width()))
            # self.settings.setValue("toolbars/icon_size", self.tab_arch.toolbars_icon_size())
            self.settings.setValue("main_window/state", self.saveState())
            self.settings.setValue("main_window/geometry", self.saveGeometry())

            event.accept()
            super().closeEvent(event)

        else:

            event.ignore()
