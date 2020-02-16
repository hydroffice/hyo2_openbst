import shutil
import unittest

from netCDF4 import Dataset
from pathlib import Path
from hyo2.abc.lib.testing_paths import TestingPaths

from hyo2.openbst.lib.project import Project
from hyo2.openbst.lib.processing.process_management.process_manager import ProcessManager, ProcessStageStatus
from hyo2.openbst.lib.processing.process_methods.dicts import ProcessMethods

# TODO: Runs slow due to writing to disk and processing. Maybe testing better suited to subtests() or just some
#  refactor to make the code better


class TestProcessingManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.ext = ".openbst"
        cls.testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
        cls.test_dir = cls.testing.output_data_folder().joinpath("test_process_manager")
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        cls.sonar_file_path = cls.testing.download_data_folder().joinpath('raw_reson', '20190321_185116.s7k')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
        cls.test_dir = cls.testing.output_data_folder().joinpath("test_process_manager")
        shutil.rmtree(cls.test_dir, ignore_errors=False)

    def test__init__(self):
        pm = ProcessManager()
        self.assertEqual(pm.step, 0)
        self.assertEqual(pm.parent_process, pm.root)
        self.assertFalse(pm.calculation_in_progress)
        self.assertIsNone(pm.current_process)
        self.assertIsNone(pm._status)

    def test_start_process(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("start_process" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.RAWDECODE, nc_process=nc, parameter_object=params)

        self.assertTrue(pm.calculation_in_progress)
        self.assertIsNotNone(pm._status)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_end_process(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("end_process" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.RAWDECODE, nc_process=nc, parameter_object=params)
        pm.end_process()
        self.assertFalse(pm.calculation_in_progress)
        self.assertIsNone(pm.current_process)
        self.assertIsNone(pm._status)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_reset(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("reset_process" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.raw_decode()

        pm = self.prj.process.proc_manager
        pm.reset_process()
        self.assertEqual(pm.step, 0)
        self.assertEqual(pm.parent_process, pm.root)
        self.prj.info.remove_nc_file()

    # Testing Node types
    def test_root_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("root_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.RAWDECODE, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.ROOTNODE)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_new_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("new_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.raw_decode()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.STATICGAIN, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.NEWNODE)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_current_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("current_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.raw_decode()
        self.prj.static_gain_correction()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.STATICGAIN, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.CURRENTNODE)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_modified_current_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("modified_current_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.parameters.rawdecode.use_window = False
        self.prj.parameters.rawdecode.sample_window_size = 10
        self.prj.raw_decode()
        self.prj.parameters.rawdecode.use_window = True

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.RAWDECODE, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.MODIFIEDCURRENTNODE)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_old_root_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("old_root_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.raw_decode()

        pm = self.prj.process.proc_manager
        pm.reset_process()
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.RAWDECODE, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.OLDROOTNODE)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_child_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("child_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.raw_decode()
        self.prj.static_gain_correction()
        self.prj.process.proc_manager.reset_process()
        self.prj.raw_decode()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.STATICGAIN, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.CHILDNODE)
        self.prj.info.remove_nc_file()
        nc.close()

    def test_ancestor_node(self):
        self.prj = Project(prj_path=self.test_dir.joinpath("ancestor_node" + self.ext), force_prj_creation=True)
        self.prj.add_raw(self.sonar_file_path)
        self.prj.check_health()
        self.prj.raw_decode()
        self.prj.static_gain_correction()

        pm = self.prj.process.proc_manager
        params = self.prj.parameters
        nc_path = self.prj.process.path.joinpath(self.prj.process.raw_process_list[0] + '.nc')
        nc = Dataset(filename=nc_path, mode='a')
        pm.start_process(process_type=ProcessMethods.RAWDECODE, nc_process=nc, parameter_object=params)

        self.assertEqual(pm._status, ProcessStageStatus.ANCESTORNODE)
        self.prj.info.remove_nc_file()
        nc.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestProcessingManager))
    return s
