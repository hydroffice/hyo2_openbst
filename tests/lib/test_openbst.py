import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.setup import Setup
from hyo2.openbst.lib.openbst import OpenBST


class TestLibOpenBST(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_name = "test_setup"
        cls.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

        # remove existing test setup
        setup_path = Setup.make_setup_path(setup_name=cls.setup_name,
                                           setups_folder=Setup.make_setups_folder(root_folder=OpenBST.root_folder()))
        if os.path.exists(setup_path):
            os.remove(setup_path)

    def test__init__(self):
        openbst = OpenBST(setup_name=self.setup_name)
        self.assertTrue(openbst.setup is not None)
        self.assertTrue(openbst.prj is not None)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibOpenBST))
    return s
