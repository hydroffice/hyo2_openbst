from datetime import datetime
from pathlib import Path
from time import sleep
import unittest

from hyo2.abc.lib.testing_paths import TestingPaths
# noinspection PyUnresolvedReferences
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.setup import Setup
from hyo2.openbst.lib.openbst import OpenBST


class TestLibSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_name = "test_setup"
        cls.testing = TestingPaths(
            root_folder=Path(__file__).parent.parent.parent.resolve())
        cls.root_folder = cls.testing.output_data_folder()

    def test__init__(self):
        _ = Setup(name=self.setup_name + 'init', prj_name=self.setup_name + 'init',
                  setups_folder=OpenBST.setups_folder(),
                  force_setup_creation=True)
        _.remove_nc_file()

    def test_list_setup_names(self):
        _ = Setup(name=self.setup_name + 'list', prj_name=self.setup_name + 'list',
                  setups_folder=OpenBST.setups_folder(),
                  force_setup_creation=True)
        setup_names = Setup.list_setup_names(root_folder=self.root_folder)
        self.assertGreaterEqual(len(setup_names), 0)

    def test_setup_name(self):
        setup = Setup(name=self.setup_name + 'name', prj_name=self.setup_name + 'name',
                      setups_folder=OpenBST.setups_folder(),
                      force_setup_creation=True)
        self.assertTrue(setup.name == self.setup_name + 'name')
        setup.remove_nc_file()

    def test_setup_version(self):
        setup = Setup(name=self.setup_name + 'version', prj_name=self.setup_name + 'version',
                      setups_folder=OpenBST.setups_folder(),
                      force_setup_creation=True)
        self.assertEqual(len(setup.version.split(".")), 3)
        setup.remove_nc_file()

    def test_setup_created(self):
        setup = Setup(name=self.setup_name + 'created', prj_name=self.setup_name + 'created',
                      setups_folder=OpenBST.setups_folder(),
                      force_setup_creation=True)
        self.assertGreater(setup.created, datetime(1970, 1, 1))
        setup.remove_nc_file()

    def test_setup_modified(self):
        setup = Setup(name=self.setup_name + 'modified', prj_name=self.setup_name + 'modified',
                      setups_folder=OpenBST.setups_folder(),
                      force_setup_creation=True)
        self.assertGreater(setup.modified, datetime(1970, 1, 1))
        sleep(1)
        setup.updated()
        self.assertGreater(setup.modified, setup.created)
        setup.remove_nc_file()

    def test_setup_path(self):
        setup = Setup(name=self.setup_name + 'path', prj_name=self.setup_name + 'path',
                      setups_folder=OpenBST.setups_folder(),
                      force_setup_creation=True)
        self.assertTrue(setup.path.exists())
        setup.remove_nc_file()

    def test_current_project(self):
        setup = Setup(name=self.setup_name + 'current', prj_name=self.setup_name + 'current',
                      setups_folder=OpenBST.setups_folder(),
                      force_setup_creation=True)
        self.assertGreater(len(setup.current_project), 0)
        setup.remove_nc_file()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibSetup))
    return s
