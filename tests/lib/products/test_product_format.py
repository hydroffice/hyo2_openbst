import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.products.product_format import ProductFormat, ProductFormatType


class FakeFormat(ProductFormat):

    def read_data_types(self, data_types: list) -> dict:
        return dict()

    def save_data_types(self, data_layers: dict) -> bool:
        return False


class TestLibFormatType(unittest.TestCase):

    def test_all(self):
        for fmt_type in ProductFormatType:
            self.assertGreaterEqual(fmt_type.value, 0)


class TestLibProductFormat(unittest.TestCase):

    def setUp(self):
        self.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)))

    def test_retrieve_spatial_info_with_gdal(self):

        for input_path in self.testing.input_test_files(ext=".tif"):
            fmt = FakeFormat(path=input_path)
            success = fmt.retrieve_spatial_info_with_gdal()
            self.assertTrue(success)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProductFormat))
    return s
