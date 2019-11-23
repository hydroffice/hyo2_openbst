import logging
from pathlib import Path

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.logging import set_logging
from hyo2.openbst.lib import lib_info
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.project import Project

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parent.parent.parent.resolve())
prj_path = Path(Helper(lib_info=lib_info).package_folder()).joinpath('projects', 'default.openbst')
logger.debug("project path: %s" % prj_path)

if not prj_path.exists():
    raise RuntimeError("missing projects folder: %s" % prj_path)

prj = Project(prj_path=prj_path)
logger.debug("\n%s" % prj)
