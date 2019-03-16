import os
import unittest
import math

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.products.product_layer import ProductLayer
from hyo2.openbst.lib.products.product_format import ProductFormatType
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType


class TestLibProductLayer(unittest.TestCase):

    def setUp(self):
        self.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)))

    def test_init(self):
        layer_type = ProductLayerType.UNKNOWN
        format_type = ProductFormatType.UNKNOWN
        layer = ProductLayer(layer_type=layer_type, format_type=format_type)
        self.assertEqual(layer.layer_type, layer_type)
        self.assertEqual(layer.format_type, format_type)
        self.assertFalse(layer.modified)

        self.assertFalse(layer.is_bathymetry())
        self.assertFalse(layer.is_uncertainty())
        self.assertFalse(layer.is_designated_soundings())
        self.assertFalse(layer.is_mosaic())

        self.assertFalse(layer.is_raster())
        self.assertFalse(layer.is_vector())

        self.assertEqual(layer.array, None)
        self.assertTrue(math.isnan(layer.array_min))
        self.assertTrue(math.isnan(layer.array_max))
        self.assertEqual(len(layer.features), 0)
        self.assertEqual(len(layer.features_x), 0)
        self.assertEqual(len(layer.features_y), 0)
        self.assertEqual(layer.feature_at_row_col(0, 0), None)

        layer.modified = True
        self.assertTrue(layer.modified)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProductLayer))
    return s
