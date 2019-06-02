import logging
import os
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.project_info import ProjectInfo

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
prj_path = Path(testing.output_data_folder()).joinpath("default.openbst")
prj_path.mkdir(parents=True, exist_ok=True)
# logger.debug("project path: %s" % prj_path)

pi = ProjectInfo(prj_path=prj_path)
pi.updated()

logger.debug("\n%s" % pi)
