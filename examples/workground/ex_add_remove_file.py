import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# Set up project
testing = TestingPaths(root_folder=Path(__file__).parents[2].resolve())
bst = OpenBST(setup_name="test")
bst.open_root_folder()

# Add a file
raw_path = testing.download_data_folder().joinpath('reson', '20190321_185116.s7k')
bst.prj.add_raw(raw_path)

raw_path = testing.download_data_folder().joinpath('reson', '20190730_144835.s7k')
bst.prj.add_raw(raw_path)

# Remove a file
bst.prj.remove_raw(raw_path)
