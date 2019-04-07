import numpy as np
import unittest

from PySide2 import QtCore, QtWidgets

# import logging
# logging.basicConfig(level=logging.DEBUG)

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.lib.products.formats.product_format_type import ProductFormatType
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType
from hyo2.openbst.lib.products.product_layer import ProductLayer
from hyo2.openbst.app.dialogs.array_explorer.array_explorer import ArrayExplorer


@unittest.skipIf(Helper.is_linux(), "Skip Linux")
class TestAppArrayExplorer(unittest.TestCase):

    def test_visibility(self):

        # noinspection PyUnresolvedReferences
        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        mw = QtWidgets.QMainWindow()
        mw.show()

        layer = ProductLayer(format_type=ProductFormatType.UNKNOWN, layer_type=ProductLayerType.UNKNOWN)
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
