from datetime import datetime
import os
import shutil
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.project import Project


class TestLibProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
        cls.prj_path = os.path.join(cls.testing.output_data_folder(), "test.openbst")

        # remove existing test setup
        if os.path.exists(cls.prj_path):
            shutil.rmtree(cls.prj_path)

    def test__init__(self):
        _ = Project(prj_path=self.prj_path)

    def test_project_path(self):
        prj = Project(prj_path=self.prj_path)
        self.assertTrue(os.path.exists(prj.project_path))

    def test_project_name(self):
        prj = Project(prj_path=self.prj_path)
        self.assertGreater(len(prj.project_name), 0)

    def test_project_info_path(self):
        prj = Project(prj_path=self.prj_path)
        self.assertTrue(os.path.exists(prj.project_info_path))

    def test_project_version(self):
        prj = Project(prj_path=self.prj_path)
        self.assertEqual(len(prj.project_version.split(".")), 3)

    def test_proejct_creation(self):
        prj = Project(prj_path=self.prj_path)
        self.assertGreater(prj.project_creation, datetime(1970, 1, 1))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProject))
    return s
