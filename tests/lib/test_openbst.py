from pathlib import Path
import unittest

from hyo2.abc.lib.testing_paths import TestingPaths
# noinspection PyUnresolvedReferences
from hyo2.openbst.app import app_info  # for GDAL data
from hyo2.openbst.lib.setup import Setup
from hyo2.openbst.lib.openbst import OpenBST


class TestLibOpenBST(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_name = "test_setup"
        cls.testing = TestingPaths(root_folder=Path(__file__).parent.parent.parent.resolve())

        # remove existing test setup
        setup_path = Setup.make_setup_path(setup_name=cls.setup_name,
                                           setups_folder=OpenBST.setups_folder())
        if setup_path.exists():
            setup_path.unlink()

    def test__init__(self):
        openbst = OpenBST(setup_name=self.setup_name)
        self.assertTrue(openbst.setup is not None)
        self.assertTrue(openbst.prj is not None)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibOpenBST))
    return s
