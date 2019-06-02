from datetime import datetime
import os
from pathlib import Path
import shutil
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.project import ProjectInfo


class TestLibProjectInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
        cls.prj_path = Path(cls.testing.output_data_folder()).joinpath("test.openbst")
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
