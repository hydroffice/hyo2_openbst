import numpy as np
import unittest

from PySide2 import QtCore, QtWidgets

# import logging
# logging.basicConfig(level=logging.DEBUG)

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.lib.sources.format import FormatType
from hyo2.openbst.lib.sources.layer_type import LayerType
from hyo2.openbst.lib.sources.layer import Layer
from hyo2.openbst.app.dialogs.array_explorer.array_explorer import ArrayExplorer


@unittest.skipIf(Helper.is_linux(), "Skip Linux")
class TestAppArrayExplorer(unittest.TestCase):

    def test_visibility(self):

        # noinspection PyUnresolvedReferences
        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        mw = QtWidgets.QMainWindow()
        mw.show()

        layer = Layer(format_type=FormatType.UNKNOWN, layer_type=LayerType.UNKNOWN)
        layer.array = np.zeros((20, 30, 40), dtype=np.float32)
        d = ArrayExplorer(layer=layer, parent=mw, with_menu=True, with_info_button=True, with_help_button=True)
        # noinspection PyCallByClass,PyTypeChecker
        QtCore.QTimer.singleShot(1, d.accept)
        ret = d.exec_()
        self.assertGreaterEqual(ret, 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAppArrayExplorer))
    return s
