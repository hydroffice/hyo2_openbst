import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.products.product import Product
from hyo2.openbst.lib.products.product_format_bag import ProductFormatBag


class TestLibProductFormatBag(unittest.TestCase):

    def setUp(self):
        self.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)))

    def test_read(self):

        for input_path in self.testing.input_test_files(ext=".bag"):
            layer_types = list(Product.retrieve_layer_and_format_types(input_path).keys())
            fmt = ProductFormatBag(path=input_path)
            layers = fmt.read_data_types(layer_types=layer_types)
            self.assertGreater(len(layers), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProductFormatBag))
    return s
