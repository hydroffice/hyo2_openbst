import logging
import os

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.project import Project

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

load_kmalls = True
load_bags = False

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

prj = Project()

if load_kmalls:
    for input_path in testing.download_test_files(ext=".kmall"):
        prj.add_raw_source(input_path)

if load_bags:
    for input_path in testing.download_test_files(ext=".bag"):
        prj.load_product_from_source(input_path)

logger.debug("\n%s" % prj)
