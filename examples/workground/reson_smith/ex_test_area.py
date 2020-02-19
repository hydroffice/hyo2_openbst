import logging

from pathlib import Path

from hyo2.openbst.lib.openbst import OpenBST
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.processing.process_methods.area_correction import AreaCorrectionEnum

logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())

bst = OpenBST(prj_name="test_area", force_new=True).prj

raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()

# Test 1: Check we meet requirements = False
bst.area_correction()

# Test 2: Method: Flat Seafloor assumption
bst.raw_decode()
bst.interpolation()
bst.raytrace()
bst.area_correction()
