import logging
import os
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.project import Project

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

load_alls = True
load_kmalls = True
load_bags = True

testing = TestingPaths(root_folder=Path(__file__).parent.parent.parent.resolve())
prj_path = testing.output_data_folder().joinpath("default.openbst")
logger.debug("project path: %s" % prj_path)

prj = Project(prj_path=prj_path)

if load_alls:
    for input_path in testing.download_test_files(ext=".all"):
        prj.add_raw(input_path)

    for input_path in testing.download_test_files(ext=".all"):
        prj.remove_raw(input_path)
        break

if load_kmalls:
    for input_path in testing.download_test_files(ext=".kmall"):
        prj.add_raw(input_path)

if load_bags:
    for input_path in testing.download_test_files(ext=".bag"):
        prj.add_product(input_path)

    for idx, input_path in enumerate(testing.download_test_files(ext=".bag")):
        if idx == 1:
            prj.remove_product(input_path)

logger.debug("\n%s" % prj)
