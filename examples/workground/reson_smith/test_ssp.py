import logging

from pathlib import Path

from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.auxilaries.ssp import SSP
from hyo2.abc.lib.testing_paths import TestingPaths

logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
svp_path = testing.download_data_folder().joinpath('ssp', 'SBE19plus_01907633_2019_07_30_cast4.svp')
svp_fail_path = testing.download_data_folder().joinpath('ssp','SBE19plus_01907633_2019_07_30_cast4.svc')
# TEST 1: Create SSP class
ssp = SSP()

# TEST 2: Read SVP = True
did_it_work = ssp.read(data_path=svp_path)
print(did_it_work)

# TEST 3: Extension Check = False
did_it_work = ssp.read(data_path=svp_fail_path)
print(did_it_work)

# TEST 4: Add a profile to the project = True
bst = OpenBST(prj_name="test_ssp", force_new=True).prj
did_it_work = bst.process.auxiliary_files.add_ssp(path=svp_path)
print(did_it_work)

# Test 5: Delete a profile = True
did_it_work = bst.process.auxiliary_files.remove_ssp(path=svp_path)
print(did_it_work)