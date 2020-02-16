import unittest

from pathlib import Path

from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.project import Project
from hyo2.openbst.lib.processing.auxilaries.calibration import Calibration


class TestCalibration(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.ext = '.openbst'
        cls.testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
        cls.test_dir = cls.testing.output_data_folder()
        cls.calib_files = cls.testing.download_test_files('.csv', subfolder='calibration')
        cls.calib_path: Path = cls.calib_files[0]

    def test__init__(self):
        _ = Calibration()

    def test_read(self):
        cal = Calibration()
        self.assertTrue(cal.read(data_path=self.calib_path))

    def test_ext_check(self):
        path_fail = self.calib_path.parent.joinpath('test.tst')
        cal = Calibration()
        self.assertFalse(cal.check_ext(data_path=path_fail))

    def test_add_profile(self):
        prj = Project(prj_path=self.test_dir.joinpath("add_profile" + self.ext), force_prj_creation=True)
        self.assertTrue(prj.process.auxiliary_files.add_calibration(path=self.calib_path))

    def test_remove_profile(self):
        prj = Project(prj_path=self.test_dir.joinpath("remove_profile" + self.ext), force_prj_creation=True)
        prj.process.auxiliary_files.add_calibration(path=self.calib_path)
        self.assertTrue(prj.process.auxiliary_files.remove_calibration(path=self.calib_path))