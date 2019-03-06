import unittest

from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.plotting import Plotting


class TestLibPlotting(unittest.TestCase):

    def test_default_init(self):
        _ = Plotting()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibPlotting))
    return s
