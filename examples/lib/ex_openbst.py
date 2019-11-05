import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

load_alls = False
load_kmalls = False
load_bags = False

testing = TestingPaths(root_folder=Path(__file__).parent.parent.parent.resolve())

bst = OpenBST(setup_name="trial")
# logger.debug("setups: %s, projects: %s" % (bst.setups_list, bst.projects_list, ))
bst.open_root_folder()

if load_alls:
    for input_path in testing.download_test_files(ext=".all"):
        bst.prj.add_raw(input_path)

if load_kmalls:
    for input_path in testing.download_test_files(ext=".kmall"):
        bst.prj.add_raw(input_path)

if load_bags:
    for input_path in testing.download_test_files(ext=".bag"):
        bst.prj.add_product(input_path)

logger.debug("\n%s" % bst)
