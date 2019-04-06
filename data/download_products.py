import logging
import os
import shutil
from hyo2.abc.lib.ftp import Ftp

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

clear_download_folder = False

# list of files to download
data_files = [
    "bathy0.asc",
    "bathy0.prj",
    "bathy0.bag",

    "bathy1.bag",

    "mosaic0.asc",
    "mosaic0.prj",
]

# create an empty `download` folder
download_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "download")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)
elif clear_download_folder:
    shutil.rmtree(download_folder)
    os.makedirs(download_folder)
products_folder = os.path.join(download_folder, "products")
if not os.path.exists(products_folder):
    os.makedirs(products_folder)
elif clear_download_folder:
    shutil.rmtree(products_folder)
    os.makedirs(products_folder)

# actually downloading the file with wget
for fid in data_files:

    data_src = os.path.join("fromccom/hydroffice/openbst/testdata/products", fid)
    data_dst = os.path.abspath(os.path.join(products_folder, fid))
    print("> downloading %s to %s" % (data_src, data_dst))

    try:
        ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False)
        ftp.get_file(data_src, data_dst, unzip_it=False)
        ftp.disconnect()

    except Exception as e:
        logger.error('while downloading %s: %s' % (fid, e))
