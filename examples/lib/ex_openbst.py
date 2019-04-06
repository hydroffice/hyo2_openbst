import logging
import os

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.openbst import OpenBST

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

load_alls = False
load_kmalls = True
load_bags = False

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

prj = OpenBST(setup_name="test")

# if load_alls:
#     for input_path in testing.download_test_files(ext=".all"):
#         prj.add_raw_source(input_path)
#
# if load_kmalls:
#     for input_path in testing.download_test_files(ext=".kmall"):
#         prj.add_raw_source(input_path)
#
# if load_bags:
#     for input_path in testing.download_test_files(ext=".bag"):
#         prj.load_product_from_source(input_path)

logger.debug("\n%s" % prj)
