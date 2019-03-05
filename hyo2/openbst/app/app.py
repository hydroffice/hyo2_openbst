import logging
import sys
import traceback

from PySide2 import QtCore, QtWidgets

from hyo2.abc.app.app_style import AppStyle
from hyo2.openbst import name as app_name
from hyo2.openbst.app.main_window import MainWindow


def set_logging(default_logging=logging.WARNING, hyo2_logging=logging.INFO, openbst_logging=logging.DEBUG):
    logging.basicConfig(
        level=default_logging,
        format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s"
    )
    logging.getLogger("hyo2").setLevel(hyo2_logging)
    logging.getLogger("hyo2.openbst").setLevel(openbst_logging)


set_logging()
logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    logger.info("Qt error: %s [%s] -> %s"
                % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def main():

    sys.argv.append("--disable-web-security")  # temporary fix for CORS warning (QTBUG-70228)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('%s' % app_name)
    app.setOrganizationName("HydrOffice")
    app.setOrganizationDomain("hydroffice.org")
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWindow()
    main_win.show()

    sys.excepthook = main_win.exception_hook  # install the exception hook

    main_win.raise_()  # to raise the window on OSX

    sys.exit(app.exec_())
