import logging
import sys
import traceback

from PySide2 import QtCore, QtWidgets

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.app_style import AppStyle
from hyo2.openbst.app.arch import app_info
from hyo2.openbst.app.arch.arch_window import ArchWindow


set_logging(ns_list=["hyo2.openbst"])
logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    if "Cannot read property 'id' of null" in message:
        return
    logger.info("Qt error: %s [%s] -> %s"
                % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def main():

    sys.argv.append("--disable-web-security")  # temporary fix for CORS warning (QTBUG-70228)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(app_info.app_name)
    app.setOrganizationName("HydrOffice")
    app.setOrganizationDomain("hydroffice.org")
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = ArchWindow(standalone=True)
    main_win.show()

    sys.excepthook = main_win.exception_hook  # install the exception hook

    main_win.raise_()  # to raise the window on OSX

    sys.exit(app.exec_())
