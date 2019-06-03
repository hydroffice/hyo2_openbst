from datetime import datetime
from pathlib import Path
import unittest

from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.setup import Setup


class TestLibSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_name = "test_setup"
        cls.testing = TestingPaths(
            root_folder=Path(__file__).parent.parent.parent.resolve())
        cls.root_folder = cls.testing.output_data_folder()

        # remove existing test setup
        setup_path = Setup.make_setup_path(setup_name=cls.setup_name,
                                           setups_folder=Setup.make_setups_folder(root_folder=cls.root_folder))
        if setup_path.exists():
            setup_path.unlink()

    def test__init__(self):
        _ = Setup(name=self.setup_name, root_folder=self.root_folder)

    def test_list_setup_names(self):
        setup_names = Setup.list_setup_names(root_folder=self.root_folder)
        self.assertGreater(len(setup_names), 0)

    def test_setup_name(self):
        setup = Setup(name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(setup.name == self.setup_name)

    def test_setup_version(self):
        setup = Setup(name=self.setup_name, root_folder=self.root_folder)
        self.assertEqual(len(setup.version.split(".")), 3)

    def test_setup_created(self):
        setup = Setup(name=self.setup_name, root_folder=self.root_folder)
        self.assertGreater(setup.created, datetime(1970, 1, 1))

    def test_setup_modified(self):
        setup = Setup(name=self.setup_name, root_folder=self.root_folder)
        self.assertGreater(setup.modified, datetime(1970, 1, 1))
        setup.updated()
        self.assertGreater(setup.modified, setup.created)

    def test_setup_path(self):
        setup = Setup(name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(setup.path.exists())

    def test_current_project(self):
        setup = Setup(name=self.setup_name, root_folder=self.root_folder)
        self.assertGreater(len(setup.current_project), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibSetup))
    return s
