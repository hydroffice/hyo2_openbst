import logging
import os
import unittest
import shutil

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.project import Project


class TestLibProject(unittest.TestCase):

    def setUp(self):
        self.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

    def test_default_init(self):
        _ = Project()

    def test_output_folder(self):
        prj = Project()

        self.assertTrue(os.path.exists(prj.output_folder))
        with self.assertRaises(RuntimeError):
            prj.output_folder = "X:/Fake/Path"

        prj.output_folder = os.path.dirname(__file__)
        self.assertTrue(os.path.exists(prj.output_folder))

    def test_raw_folder(self):
        prj = Project()

        self.assertTrue(os.path.exists(prj.raw_folder))

        test_folder = os.path.join(os.path.dirname(__file__), "test_raw_folder")
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
        os.mkdir(test_folder)
        prj.output_folder = test_folder
        self.assertTrue(os.path.exists(prj.raw_folder))
        self.assertTrue(prj.is_raw_folder_empty())
        shutil.rmtree(test_folder)

    def test_export_folder(self):
        prj = Project()

        self.assertTrue(os.path.exists(prj.export_folder))

        test_folder = os.path.join(os.path.dirname(__file__), "test_export_folder")
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
        os.mkdir(test_folder)
        prj.output_folder = test_folder
        self.assertTrue(os.path.exists(prj.export_folder))
        shutil.rmtree(test_folder)

    def test_is_vr(self):
        input_path = self.testing.download_test_files(ext=".bag")[0]
        self.assertFalse(Project.is_product_vr(path=input_path))

    def test_load_from_source_and_save(self):

        prj = Project()

        # BAG
        for input_path in self.testing.download_test_files(ext=".bag"):
            prj.load_product_from_source(input_path)
            self.assertGreater(len(prj.product_layers_dict), 0)

            output_path = os.path.join(self.testing.output_data_folder(),
                                       "PRJ_" + os.path.basename(input_path))
            success = prj.save_product_layer_by_key(layer_key=list(prj.product_layers_dict.keys())[0],
                                                    output_path=output_path,
                                                    open_folder=False)
            self.assertTrue(success)

        # GeoTIFF
        for input_path in self.testing.download_test_files(ext=".tif"):
            prj.load_product_from_source(input_path)
            self.assertGreater(len(prj.product_layers_dict), 0)

            output_path = os.path.join(self.testing.output_data_folder(),
                                       "PRJ_" + os.path.basename(input_path))
            success = prj.save_product_layer_by_key(layer_key=list(prj.product_layers_dict.keys())[0],
                                                    output_path=output_path,
                                                    open_folder=False)

        # ASCII Grid
        for input_path in self.testing.download_test_files(ext=".asc"):
            prj.load_product_from_source(input_path)
            self.assertGreater(len(prj.product_layers_dict), 0)

            output_path = os.path.join(self.testing.output_data_folder(),
                                       "PRJ_" + os.path.basename(input_path))
            success = prj.save_product_layer_by_key(layer_key=list(prj.product_layers_dict.keys())[0],
                                                    output_path=output_path,
                                                    open_folder=False)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProject))
    return s
