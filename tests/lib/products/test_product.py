import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.products.product import Product
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType
from hyo2.openbst.lib.products.product_format import ProductFormatType


class TestLibProductFormat(unittest.TestCase):

    def setUp(self):
        self.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)))

    def test_retrieve_raster_types(self):

        # BAG
        for input_path in self.testing.download_test_files(ext=".bag"):
            types = Product.retrieve_layer_and_format_types(input_path)
            self.assertEqual(len(types), 3)
            for raster_type in types:
                self.assertTrue(raster_type in [ProductLayerType.BATHYMETRY,
                                                ProductLayerType.UNCERTAINTY,
                                                ProductLayerType.DESIGNATED])
                self.assertEqual(types[raster_type], ProductFormatType.BAG)

        # GeoTiff
        for input_path in self.testing.download_test_files(ext=".tif"):
            types = Product.retrieve_layer_and_format_types(input_path)
            self.assertEqual(len(types), 1)
            for raster_type in types:
                self.assertTrue(raster_type in [ProductLayerType.MOSAIC])
                self.assertEqual(types[raster_type], ProductFormatType.GEOTIFF)

        # ASCII Grid
        for input_path in self.testing.download_test_files(ext=".asc"):
            types = Product.retrieve_layer_and_format_types(input_path)
            self.assertEqual(len(types), 1)
            for raster_type in types:
                self.assertTrue(raster_type in [ProductLayerType.BATHYMETRY])
                self.assertEqual(types[raster_type], ProductFormatType.ASC_GRID)

            types = Product.retrieve_layer_and_format_types(input_path, hint_type=ProductLayerType.MOSAIC)
            self.assertEqual(len(types), 1)
            for raster_type in types:
                self.assertTrue(raster_type in [ProductLayerType.MOSAIC])
                self.assertEqual(types[raster_type], ProductFormatType.ASC_GRID)

    def test_load(self):

        # BAG
        for input_path in self.testing.download_test_files(ext=".bag"):
            layer_types = list(Product.retrieve_layer_and_format_types(input_path).keys())
            layers = Product.load(input_path=input_path, layer_types=layer_types,
                                  input_format=ProductFormatType.BAG)
            self.assertGreater(len(layers), 0)

        # GeoTiff
        for input_path in self.testing.download_test_files(ext=".tif"):
            layer_types = list(Product.retrieve_layer_and_format_types(input_path).keys())
            layers = Product.load(input_path=input_path, layer_types=layer_types,
                                  input_format=ProductFormatType.GEOTIFF)
            self.assertGreater(len(layers), 0)

        # ASCII Grid
        for input_path in self.testing.download_test_files(ext=".asc"):
            layer_types = list(Product.retrieve_layer_and_format_types(input_path).keys())
            layers = Product.load(input_path=input_path, layer_types=layer_types,
                                  input_format=ProductFormatType.ASC_GRID)
            self.assertGreater(len(layers), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProductFormat))
    return s
