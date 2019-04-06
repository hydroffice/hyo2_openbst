from datetime import datetime
import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.setup import Setup


class TestLibSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_name = "test_setup"
        cls.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
        cls.root_folder = cls.testing.output_data_folder()

        # remove existing test setup
        setup_path = Setup.make_setup_path(setup_name=cls.setup_name,
                                           setups_folder=Setup.make_setups_folder(root_folder=cls.root_folder))
        if os.path.exists(setup_path):
            os.remove(setup_path)

    def test__init__(self):
        _ = Setup(setup_name=self.setup_name, root_folder=self.root_folder)

    def test_setups_folder(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(os.path.exists(setup.setups_folder))

    def test_list_setup_names(self):
        setup_names = Setup.list_setup_names(root_folder=self.root_folder)
        self.assertGreater(len(setup_names), 0)

    def test_setup_name(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(setup.setup_name == self.setup_name)

    def test_setup_version(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertEqual(len(setup.setup_version.split(".")), 3)

    def test_setup_creation(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertGreater(setup.setup_creation, datetime(1970, 1, 1))

    def test_setup_path(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(os.path.exists(setup.setup_path))

    def test_projects_folder(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(os.path.exists(setup.projects_folder))

    def test_outputs_folder(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertTrue(os.path.exists(setup.outputs_folder))

    def test_current_project(self):
        setup = Setup(setup_name=self.setup_name, root_folder=self.root_folder)
        self.assertGreater(len(setup.current_project), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibSetup))
    return s
