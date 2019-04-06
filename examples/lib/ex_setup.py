import logging
import os

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.setup import Setup

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

setup = Setup(setup_name="test", root_folder=testing.output_data_folder())

logger.debug("\n%s" % setup)
