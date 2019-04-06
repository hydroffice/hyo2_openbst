import hashlib
import logging
import os
from netCDF4 import Dataset

from hyo2.abc.lib.testing import Testing

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

bst_path = os.path.normpath(os.path.join(testing.output_data_folder(), "test.bst"))
bst_raws_name = "raws"
bst_products_name = "products"

load_kmalls = True
read_kmalls = True

# file creation/access

open_mode = "w"
if os.path.exists(bst_path):
    open_mode = "a"

bst = Dataset(filename=bst_path, mode=open_mode)

logger.debug("opened in '%s' mode: [%s] %s" % (open_mode, bst.data_model, bst_path))

# root groups creation/access

bst_raws = bst.createGroup(bst_raws_name)
bst_products = bst.createGroup(bst_products_name)

if load_kmalls:
    for input_path in testing.download_test_files(ext=".kmall"):
        input_path_hash = hashlib.sha256(input_path.encode('utf-8')).hexdigest()
        logger.debug(input_path_hash)
        input_grp = bst_raws.createGroup(input_path_hash)

        input_grp.full_path = input_path

if read_kmalls:
    for idx, input_grp in enumerate(bst_raws.groups.values()):
        logger.debug("%d: %s" % (idx, input_grp.full_path))

bst.close()
