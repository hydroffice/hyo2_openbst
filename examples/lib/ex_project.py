import logging
import os
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.project import Project

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

load_alls = False
load_kmalls = False
load_bags = True

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

prj_path = Path(testing.output_data_folder()).joinpath("default.openbst")
logger.debug("project path: %s" % prj_path)

prj = Project(prj_path=prj_path)

# if load_alls:
#     for input_path in testing.download_test_files(ext=".all"):
#         prj.add_raw(input_path)
#
#     for input_path in testing.download_test_files(ext=".all"):
#         prj.remove_raw(input_path)
#         break
#
# if load_kmalls:
#     for input_path in testing.download_test_files(ext=".kmall"):
#         prj.add_raw(input_path)
#
# if load_bags:
#     for input_path in testing.download_test_files(ext=".bag"):
#         prj.add_product(input_path)
#
#     for idx, input_path in enumerate(testing.download_test_files(ext=".bag")):
#         if idx == 1:
#             prj.remove_product(input_path)
#
# logger.debug("valid raws: %s" % (prj.valid_raws()))
#
# logger.debug("\n%s" % prj)
