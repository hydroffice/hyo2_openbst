import logging

from pathlib import Path

from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.auxilaries.calibration import Calibration
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.processing.process_methods.calibration import CalibrationEnum


logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
cal_path = testing.download_data_folder().joinpath('calibration', 'chain_14m_200kHz.csv')
cal_path_fail = testing.download_data_folder().joinpath('calibration', 'chain_14m_200kHz.cvs')

bst = OpenBST(prj_name="test_cal_corr", force_new=True).prj
did_it_work = bst.process.auxiliary_files.add_calibration(path=cal_path)

raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()
# Test 1: Check that we meet requirements = False
bst.parameters.calibration.method_type = CalibrationEnum.calibration_file
bst.parameters.calibration.fit_curve = True
bst.parameters.calibration.curve_order = 4
bst.calibration()

# Test 2: Method: Calibration File, Pass = No errors
bst.raw_decode()
bst.calibration()

