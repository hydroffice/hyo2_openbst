import ftplib
import logging
import shutil

from pathlib import Path
from hyo2.abc.lib.ftp import Ftp
from hyo2.abc.lib.testing_paths import TestingPaths

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

# Set Script Parameters
clear_download_folder = False
force_dwnld = True
ftp_address = "ftp.ccom.unh.edu"
ftp_ssp_path = Path("fromccom/hydroffice/openbst/testdata/ssp")
ftp_cal_path = Path("fromccom/hydroffice/openbst/testdata/calibration")

# list of file to download
calibration_files = [
    'chain_14m_200kHz.csv'
]

ssp_files = [
    'SBE19plus_01907633_2019_07_30_cast4.svp',
    'SBE19plus_01907633_2019_07_30_cast5.svp',
    'SBE19plus_01907633_2019_07_30_cast6.svp'
]

# Manage Download folder
download_folder = TestingPaths(root_folder=Path(__file__).parents[1].resolve()).download_data_folder()
if clear_download_folder is True:
    shutil.rmtree(str(download_folder.resolve()))
download_folder.mkdir(parents=True, exist_ok=True)
ssp_folder = download_folder.joinpath("ssp")
ssp_folder.mkdir(parents=True, exist_ok=True)
calib_folder = download_folder.joinpath("calibration")
calib_folder.mkdir(parents=True, exist_ok=True)

# Download files over ftp
for fid in calibration_files:
    data_src = ftp_cal_path.joinpath(fid)
    data_dst = calib_folder.joinpath(fid)

    if data_dst.exists() is True and force_dwnld is False:
        logger.info('already downloaded: %s' % data_dst)
        continue

    print("> downloading %s to %s" % (data_src, data_dst))
    try:
        ftp = Ftp(ftp_address, show_progress=True, debug_mode=False)
        ftp.get_file(str(data_src.resolve()), str(data_dst.resolve()), unzip_it=False)
        ftp.disconnect()

    except ftplib.all_errors as e:
        logger.error("While downloading %s: %s" % (fid, e))

for fid in ssp_files:
    data_src = ftp_ssp_path.joinpath(fid)
    data_dst = ssp_folder.joinpath(fid)

    if data_dst.exists() is True and force_dwnld is False:
        logger.info('already downloaded: %s' % data_dst)
        continue

    print("> downloading %s to %s" % (data_src, data_dst))
    try:
        ftp = Ftp(ftp_address, show_progress=True, debug_mode=False)
        ftp.get_file(str(data_src.resolve()), str(data_dst.resolve()), unzip_it=False)
        ftp.disconnect()

    except ftplib.all_errors as e:
        logger.error("While downloading %s: %s" % (fid, e))