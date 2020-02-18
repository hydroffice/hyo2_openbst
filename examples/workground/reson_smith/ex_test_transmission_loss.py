import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeEnum
from hyo2.openbst.lib.processing.process_methods.transmission_loss import TransmissionLossEnum

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# Set up project
testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
bst = OpenBST(prj_name="test_tl", force_new=True).prj
# bst.open_project_folder()
raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()

# Test 1 - Fail = raw decode requirement
bst.parameters.transmissionloss.method_type = TransmissionLossEnum.spherical
bst.transmission_loss_correction()



# Raw decode
bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
bst.raw_decode()
bst.tvg_gain_correction()
bst.interpolation()
bst.raytrace()


# Test 2 - Method:Simple, Pass = No Errors
bst.transmission_loss_correction()
