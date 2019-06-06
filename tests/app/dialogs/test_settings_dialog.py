import unittest

from PySide2 import QtCore, QtWidgets

# import logging
# logging.basicConfig(level=logging.DEBUG)

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.app.dialogs.setup_dialog import SetupDialog
from hyo2.openbst.lib.openbst import OpenBST


@unittest.skipIf(Helper.is_linux(), "Skip Linux")
class TestAppSettingsDialog(unittest.TestCase):

    def test_visibility(self):

        # noinspection PyUnresolvedReferences
        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        mw = QtWidgets.QMainWindow()
        mw.show()

        d = SetupDialog(parent=mw, lib=OpenBST())
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        QtCore.QTimer.singleShot(1, d.accept)
        ret = d.exec_()
        self.assertGreaterEqual(ret, 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAppSettingsDialog))
    return s
