import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.source import Source, LayerType, FormatType


class TestLibSource(unittest.TestCase):

    def setUp(self):
        self.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

    def test_retrieve_raster_types(self):

        # BAG
        for input_path in self.testing.download_test_files(ext=".bag"):
            types = Source.retrieve_layer_and_format_types(input_path)
            self.assertEqual(len(types), 3)
            for raster_type in types:
                self.assertTrue(raster_type in [LayerType.BATHYMETRY,
                                                LayerType.UNCERTAINTY,
                                                LayerType.DESIGNATED])
                self.assertEqual(types[raster_type], FormatType.BAG)

        # GeoTiff
        for input_path in self.testing.download_test_files(ext=".tif"):
            types = Source.retrieve_layer_and_format_types(input_path)
            self.assertEqual(len(types), 1)
            for raster_type in types:
                self.assertTrue(raster_type in [LayerType.MOSAIC])
                self.assertEqual(types[raster_type], FormatType.GEOTIFF)

        # ASCII Grid
        for input_path in self.testing.download_test_files(ext=".asc"):
            types = Source.retrieve_layer_and_format_types(input_path)
            self.assertEqual(len(types), 1)
            for raster_type in types:
                self.assertTrue(raster_type in [LayerType.BATHYMETRY])
                self.assertEqual(types[raster_type], FormatType.ASC_GRID)

            types = Source.retrieve_layer_and_format_types(input_path, hint_type=LayerType.MOSAIC)
            self.assertEqual(len(types), 1)
            for raster_type in types:
                self.assertTrue(raster_type in [LayerType.MOSAIC])
                self.assertEqual(types[raster_type], FormatType.ASC_GRID)

    def test_load(self):

        # BAG
        for input_path in self.testing.download_test_files(ext=".bag"):
            layer_types = list(Source.retrieve_layer_and_format_types(input_path).keys())
            layers = Source.load(input_path=input_path, layer_types=layer_types,
                                 input_format=FormatType.BAG)
            self.assertGreater(len(layers), 0)

        # GeoTiff
        for input_path in self.testing.download_test_files(ext=".tif"):
            layer_types = list(Source.retrieve_layer_and_format_types(input_path).keys())
            layers = Source.load(input_path=input_path, layer_types=layer_types,
                                 input_format=FormatType.GEOTIFF)
            self.assertGreater(len(layers), 0)

        # ASCII Grid
        for input_path in self.testing.download_test_files(ext=".asc"):
            layer_types = list(Source.retrieve_layer_and_format_types(input_path).keys())
            layers = Source.load(input_path=input_path, layer_types=layer_types,
                                 input_format=FormatType.ASC_GRID)
            self.assertGreater(len(layers), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibSource))
    return s
