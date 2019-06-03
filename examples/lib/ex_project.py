import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.products.product import Product

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parent.parent.parent.resolve())
prj_path = testing.output_data_folder().joinpath("default.openbst")
products_path = prj_path.joinpath("products")
logger.debug("project path: %s" % prj_path)
if not products_path.exists():
    raise RuntimeError("missing products folder: %s" % products_path)

ncs = list(products_path.rglob(pattern="*.nc"))
logger.debug("nr of products: %d" % len(ncs))

# prj = Project(prj_path=prj_path)
# logger.debug("\n%s" % prj)
