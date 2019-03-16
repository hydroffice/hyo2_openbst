import unittest

from hyo2.openbst.lib.products.product_plotting import ProductPlotting


class TestLibProductPlotting(unittest.TestCase):

    def test_default_init(self):
        _ = ProductPlotting()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProductPlotting))
    return s
