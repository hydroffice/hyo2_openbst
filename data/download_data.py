import logging
import os.path
import shutil
from hyo2.abc.lib.ftp import Ftp

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

clear_download_folder = False

# list of files to download
data_files = [
    "0011_20180908_150242.all",
    "0011_20180908_150242.kmall",
    "0011_20180908_150242.xsf",

    "0015_20180908_155534.all",
    "0015_20180908_155534.kmall",
    "0015_20180908_155534.xsf",

    "0017_20180908_165908.all",
    "0017_20180908_165908.kmall",
    "0017_20180908_165908.xsf",

    "0019_20180908_175305.all",
    "0019_20180908_175305.kmall",
    "0019_20180908_175305.xsf",
]

# create an empty `downloaded` folder
downloaded_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "download")
if os.path.exists(downloaded_folder) and clear_download_folder:
    shutil.rmtree(downloaded_folder)
os.makedirs(downloaded_folder)

# actually downloading the file with wget
for fid in data_files:

    data_src = os.path.join("fromccom/hydroffice/openbst/testdata", fid)
    data_dst = os.path.abspath(os.path.join(downloaded_folder, fid))
    print("> downloading %s" % data_src)

    try:
        ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False)
        ftp.get_file(data_src, data_dst, unzip_it=False)
        ftp.disconnect()

    except Exception as e:
        logger.error('while downloading %s: %s' % (fid, e))
