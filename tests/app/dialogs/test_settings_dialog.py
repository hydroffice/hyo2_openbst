import unittest

from PySide2 import QtCore, QtWidgets

# import logging
# logging.basicConfig(level=logging.DEBUG)

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.app.dialogs.settings_dialog import SettingsDialog


@unittest.skipUnless(Helper.is_windows(), "Windows-only")
class TestAppSettingsDialog(unittest.TestCase):

    def test_visibility(self):

        # noinspection PyUnresolvedReferences
        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        mw = QtWidgets.QMainWindow()
        mw.show()

        d = SettingsDialog(parent=mw)
        # noinspection PyCallByClass,PyTypeChecker
        QtCore.QTimer.singleShot(1, d.accept)
        ret = d.exec_()
        self.assertGreaterEqual(ret, 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAppSettingsDialog))
    return s
