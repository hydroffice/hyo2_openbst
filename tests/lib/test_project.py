import os
from pathlib import Path
import unittest

from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.project import Project


class TestLibProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testing = TestingPaths(
            root_folder=Path(__file__).parent.parent.parent.resolve())
        cls.prj_path = cls.testing.output_data_folder().joinpath("test.openbst")

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
