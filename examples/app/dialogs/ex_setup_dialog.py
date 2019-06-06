import sys
import logging
from PySide2 import QtWidgets

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.app_style import AppStyle
from hyo2.openbst.app.dialogs.setup_dialog import SetupDialog
from hyo2.openbst.lib.openbst import OpenBST

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.openbst", ])

app = QtWidgets.QApplication([])
app.setStyleSheet(AppStyle.load_stylesheet())

mw = QtWidgets.QMainWindow()
mw.show()

dlg = SetupDialog(lib=OpenBST(), parent=mw)
dlg.exec_()

sys.exit(app.exec_())
