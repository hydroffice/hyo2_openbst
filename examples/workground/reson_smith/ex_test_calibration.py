import logging

from pathlib import Path

from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.auxilaries.calibration import Calibration
from hyo2.abc.lib.testing_paths import TestingPaths


logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
cal_path = testing.download_data_folder().joinpath('calibration', 'chain_14m_200kHz.csv')
cal_path_fail = testing.download_data_folder().joinpath('calibration', 'chain_14m_200kHz.cvs')

# Test 1: Create Calibration Class
cal = Calibration()

# Test 2: Read Calibration File = True
did_it_work = cal.read(data_path=cal_path)
print(did_it_work)

# Test 3: Extenstion check = False
did_it_work = cal.read(data_path=cal_path_fail)
print(did_it_work)

# TEST 4: Add a profile to the project = True
bst = OpenBST(prj_name="test_cal", force_new=True).prj
did_it_work = bst.process.auxiliary_files.add_calibration(path=cal_path)
print(did_it_work)

# Test 5: Delete a profile = True
did_it_work = bst.process.auxiliary_files.remove_calibration(path=cal_path)
print(did_it_work)