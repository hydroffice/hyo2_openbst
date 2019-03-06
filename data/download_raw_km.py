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

# create an empty `download` folder
download_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "download")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)
elif clear_download_folder:
    shutil.rmtree(download_folder)
    os.makedirs(download_folder)
raw_km_folder = os.path.join(download_folder, "raw_km")
if not os.path.exists(download_folder):
    os.makedirs(raw_km_folder)
elif clear_download_folder:
    shutil.rmtree(raw_km_folder)
    os.makedirs(raw_km_folder)

# actually downloading the file with wget
for fid in data_files:

    data_src = os.path.join("fromccom/hydroffice/openbst/testdata/raw_km", fid)
    data_dst = os.path.abspath(os.path.join(raw_km_folder, fid))
    print("> downloading %s to %s" % (data_src, data_dst))

    try:
        ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False)
        ftp.get_file(data_src, data_dst, unzip_it=False)
        ftp.disconnect()

    except Exception as e:
        logger.error('while downloading %s: %s' % (fid, e))
