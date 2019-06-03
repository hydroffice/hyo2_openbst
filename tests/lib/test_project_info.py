from datetime import datetime
from pathlib import Path
import unittest

from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.project import ProjectInfo


class TestLibProjectInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testing = TestingPaths(
            root_folder=Path(__file__).parent.parent.parent.resolve())
        cls.prj_path = cls.testing.output_data_folder().joinpath("test.openbst")
        cls.prj_path.mkdir(parents=True, exist_ok=True)

    def test__init__(self):
        _ = ProjectInfo(prj_path=self.prj_path)

    def test_path(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertTrue(pi.path.exists())

    def test_name(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreater(len(pi.name), 0)

    def test_version(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertEqual(len(pi.version.split(".")), 3)

    def test_created(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreater(pi.created, datetime(1970, 1, 1))

    def test_modified(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        mod = pi.modified
        self.assertGreater(mod, datetime(1970, 1, 1))
        pi.updated()
        self.assertTrue(mod != pi.modified)

    def test_raws(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.raws), 0)

    def test_products(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.products), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProjectInfo))
    return s
