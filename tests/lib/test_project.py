from datetime import datetime
import os
from pathlib import Path
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
        cls.prj_path = Path(cls.testing.output_data_folder()).joinpath("test.openbst")

    def test__init__(self):
        _ = Project(prj_path=self.prj_path)

    def test_project_path(self):
        prj = Project(prj_path=self.prj_path)
        self.assertTrue(prj.path.exists())

    def test_project_name(self):
        prj = Project(prj_path=self.prj_path)
        self.assertGreater(len(prj.info.name), 0)

    def test_project_info_path(self):
        prj = Project(prj_path=self.prj_path)
        self.assertTrue(prj.info.path.exists())


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProject))
    return s
