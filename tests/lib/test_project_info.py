from copy import deepcopy
from time import sleep
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
            root_folder=Path(__file__).parents[2].resolve())
        cls.prj_path = cls.testing.output_data_folder().joinpath("test.openbst")
        cls.prj_path.mkdir(parents=True, exist_ok=True)

        cls.sonar_file_path = cls.testing.download_data_folder().joinpath('reson', '20190321_185116.s7k')
        cls.ssp_path = cls.testing.download_data_folder().joinpath('ssp','20190729_184301_ssp.csv')
        cls.calibration_path = cls.testing.download_data_folder().joinpath('calibration',
                                                                           'chain_14m_200kHz.csv')

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
        mod = deepcopy(pi.modified)
        sleep(1)
        self.assertGreater(mod, datetime(1970, 1, 1))
        pi.updated()
        self.assertTrue(mod != pi.modified)

    def test_raws(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.raws), 0)

    def test_processes(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.raws), 0)

    def test_products(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.products), 0)

    def test_ssps(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.ssps), 0)

    def test_calibrations(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertGreaterEqual(len(pi.calibrations), 0)

    # Testing Add/Remove Methods
    def test_add_raw(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertTrue(pi.add_raw(path=self.sonar_file_path))
        self.assertEqual(pi.raws[pi.project_raws[0]].deleted, 0)

    def test_remove_raw(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        pi.add_raw(path=self.sonar_file_path)
        file_hash = pi.project_raws[0]
        self.assertTrue(pi.remove_raw(path=self.sonar_file_path))
        self.assertEqual(pi.raws[file_hash].deleted, 1)

    def test_add_process(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertTrue(pi.add_process(path=self.sonar_file_path))
        self.assertEqual(pi.processes[pi.project_process[0]].deleted, 0)

    def test_remove_process(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        pi.add_process(path=self.sonar_file_path)
        file_hash = pi.project_process[0]
        self.assertTrue(pi.remove_process(path=self.sonar_file_path))
        self.assertEqual(pi.processes[file_hash].deleted, 1)

    def test_add_product(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertTrue(pi.add_product(path=self.sonar_file_path))
        self.assertEqual(pi.products[pi.project_products[0]].deleted, 0)

    def test_remove_product(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        pi.add_product(path=self.sonar_file_path)
        file_hash = pi.project_products[0]
        self.assertTrue(pi.remove_product(path=self.sonar_file_path))
        self.assertEqual(pi.products[file_hash].deleted, 1)

    def test_add_ssp(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertTrue(pi.add_ssp(path=self.ssp_path))
        self.assertEqual(pi.ssps[pi.ssp_list[0]].deleted, 0)

    def test_ssp_extension(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertFalse(pi.add_ssp(path=self.sonar_file_path))

    def test_remove_ssp(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        pi.add_ssp(path=self.ssp_path)
        file_hash = pi.ssp_list[0]
        self.assertTrue(pi.remove_ssp(path=self.ssp_path))
        self.assertEqual(pi.ssps[file_hash].deleted, 1)

    def test_add_calibration(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertTrue(pi.add_calibration(path=self.calibration_path))
        self.assertEqual(pi.calibrations[pi.calibration_list[0]].deleted, 0)

    def test_calibration_extension(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        self.assertFalse(pi.add_calibration(path=self.sonar_file_path))

    def test_remove_calibration(self):
        pi = ProjectInfo(prj_path=self.prj_path)
        pi.add_calibration(path=self.calibration_path)
        file_hash = pi.calibration_list[0]
        self.assertTrue(pi.remove_calibration(path=self.calibration_path))
        self.assertEqual(pi.calibrations[file_hash].deleted, 1)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibProjectInfo))
    return s
