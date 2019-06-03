import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.setup import Setup

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parent.parent.parent)
setups_folder = testing.output_data_folder().joinpath("ex_setup")
setups_folder.mkdir(parents=True, exist_ok=True)

setup_names = Setup.list_setup_names(root_folder=setups_folder)
logger.debug("setup names: %s" % (setup_names, ))

setup = Setup(name="test", root_folder=setups_folder)
# setup.current_project = "test2"
logger.debug("\n%s" % setup)
