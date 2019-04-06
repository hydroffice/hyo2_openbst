import logging
import os

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.project import Project

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

load_alls = True
load_kmalls = True
load_bags = True

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

prj_path = os.path.join(testing.output_data_folder(), "project.openbst")

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

    for input_path in testing.download_test_files(ext=".bag"):
        prj.remove_product(input_path)
        break

logger.debug("valid raws: %s" % (prj.valid_raws()))

logger.debug("\n%s" % prj)
