import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeEnum
from hyo2.openbst.lib.processing.process_methods.tvg import TVGENUM

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# Set up project
testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
bst = OpenBST(prj_name="test_tvg", force_new=True).prj
# bst.open_project_folder()
raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()

# Test 1 - Fail = raw decode requirement
bst.parameters.tvg.method_type = TVGENUM.gain_removal_simple_tvg_curve
bst.tvg_gain_correction()


# Raw decode
bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
bst.raw_decode()

# Test 2 - Method:Simple, Pass = No Errors
bst.parameters.tvg.method_type = TVGENUM.gain_removal_simple_tvg_curve
bst.tvg_gain_correction()

# Test 3 - Method:From Manufacturer, Pass = No Errors
bst.parameters.tvg.method_type = TVGENUM.gain_removal_tvg_curve_from_manufacturer
bst.tvg_gain_correction()

# Test 4 - Method:From Runtime gains ,Pass = No Errors
bst.parameters.tvg.method_type = TVGENUM.gain_removal_tvg_curve_generated_from_gains
bst.tvg_gain_correction()
