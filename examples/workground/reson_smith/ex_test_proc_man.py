import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeEnum
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainEnum
from hyo2.openbst.lib.processing.process_methods.source_level import SourceLevelEnum

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)


# Set up project
def setup():
    testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
    prj = OpenBST(prj_name="test_proc_man", force_new=True).prj
    # bst.open_project_folder()
    raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
    prj.add_raw(raw_path)

    # import raws via project health check
    prj.check_health()
    return prj


if __name__ == '__main__':

    # Run 1 - ROOTNODE, NEWNODE, NEWNODE
    bst = setup()

    bst.parameters.rawdecode.use_window = False
    bst.parameters.rawdecode.sample_window_size = 10
    bst.raw_decode()                                # ROOT NODE

    bst.parameters.source_level.method_type = SourceLevelEnum.gain_removal
    bst.source_level_correction()                   # NEW NODE

    bst.parameters.static_gains.method_type = StaticGainEnum.gain_removal
    bst.static_gain_correction()                    # NEW NODE
    print('---------------------------')

    # Run 2 - CURRENTNODE, MODIFIEDCURRENTNODE
    bst.parameters.static_gains.method_type = StaticGainEnum.gain_removal
    bst.static_gain_correction()                    # CURRENT NODE

    bst.parameters.static_gains.method_type = StaticGainEnum.gain_addition
    bst.static_gain_correction()                    # MODIFIED CURRENT NODE
    print('---------------------------')

    # Run 3 - reset, OLDROOTNODE, CHILDNODE, ANCESTORNODE
    bst.process.proc_manager.reset_process()

    bst.parameters.rawdecode.use_window = False
    bst.parameters.rawdecode.sample_window_size = 10
    bst.raw_decode()                                # OLD ROOT NODE

    bst.parameters.source_level.method_type = SourceLevelEnum.gain_removal
    bst.source_level_correction()                   # CHILD NODE

    bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
    bst.raw_decode()                                # ANCESTOR NODE
    print('-----------------------------')

    # Run 4 - reset, ROOTNODE, NEWNODE
    bst.process.proc_manager.reset_process()

    bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
    bst.raw_decode()                                # ROOT NODE

    bst.source_level_correction()                   # NEWNODE


    bst.parameters.static_gains.method_type = StaticGainEnum.gain_removal
    bst.static_gain_correction()                    # NEW NODE
