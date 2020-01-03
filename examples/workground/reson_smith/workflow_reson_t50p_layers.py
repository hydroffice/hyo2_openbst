import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.raw_decoding import RawDecodeEnum

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# Set up project
testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
bst = OpenBST(prj_name="default", force_new=True).prj
bst.open_project_folder()
raw_path = testing.download_data_folder().joinpath('reson', '20190730_144835.s7k')
bst.add_raw(raw_path)

# import raws via project health check
bst.check_health()

# Raw decode
bst.parameters.rawdecode.use_window = False
bst.parameters.rawdecode.sample_window_size = 10
bst.raw_decode()

# test 2
bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
bst.raw_decode()