import glob
import logging
import os

from netCDF4 import Dataset
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.parameters import Parameters
from hyo2.openbst.lib.processing.raw_decoding import RawDecoding

logger = logging.getLogger(__name__)


class Process:

    ext = ".nc"

    def __init__(self, process_path: Path) -> None:
        self._path = process_path
        self._step = 00
        self._prior_process = ''

    @property
    def path(self) -> Path:
        return self._path

    @property
    def step(self) -> int:
        return self._step

    @step.setter
    def step(self, step):
        self._step = step

    @property
    def prior_process(self) -> str:
        return self._prior_process

    @prior_process.setter
    def prior_process(self, current_process):
        self._prior_process = current_process

    @property
    def raw_process_list(self) -> list:
        raw_process_list = list()
        for hash_file in glob.glob(str(self._path.joinpath("*" + Process.ext))):
            hash_path = Path(hash_file)
            raw_process_list.append(hash_path.name.split('.')[0])
        return raw_process_list

    # ## NC File Management ##
    def add_raw_process(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.raw_process_list:
            logger.info("file already in project: %s" % path)
        else:
            file_name = self.path.joinpath(path_hash + self.ext)
            raw_process = Dataset(filename=file_name, mode='w')
            NetCDFHelper.init(ds=raw_process)
            raw_process.close()
            logger.info("raw_process .nc created for added file: %s" % str(path.resolve()))
        return True

    def remove_raw_process(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raw_process_list:
            logger.info("absent: %s" % path)
            return False
        else:
            raw_process_path = self._path.joinpath(path_hash + Process.ext)
            os.remove(str(raw_process_path.resolve()))
            logger.info("raw .nc deleted for file: %s" % str(path.resolve()))
            return True

    def store_process(self, nc: Dataset, process_string: str) -> bool:
        NetCDFHelper.update_modified(ds=nc)
        nc.close()

        if process_string.split('_')[0] == '00':
            self.step = 0
        else:
            self.step += 1

        self.prior_process = process_string
        return True

    @staticmethod
    def check_raw_process(nc_process: Dataset, process_string: str) -> bool:
        processed = False

        grp_list = nc_process.groups
        if len(grp_list) != 0:
            for nc_process_step, _ in grp_list.items():
                nc_process_string = nc_process_step.split('_')  # TODO: Check that I need an index
                if nc_process_string == process_string:
                    processed = True
                    break

        return processed

    # ## Processing Methods ##
    def raw_decode(self, process_file_path: Path, raw_path: Path, parameters: Parameters):
        # create nc objects
        ds_process = Dataset(filename=process_file_path, mode='a')
        ds_raw = Dataset(filename=raw_path, mode='a')

        params_raw_decode = parameters.rawdecode

        # check process has not been calculated before
        process_name_str = params_raw_decode.process_hash()
        has_been_processd = self.check_raw_process(nc_process=ds_process, process_string=process_name_str)

        if has_been_processd is True:
            logger.debug("Processing step has been computed prior")
            return True
        else:

            bs_raw_decode = RawDecoding.decode(ds_raw=ds_raw, parameters=params_raw_decode)

            # Write data to nc file
            initial_step = 0
            nc_process_name = "%02d" % initial_step + '_' + process_name_str
            grp_process = ds_process.createGroup(nc_process_name)
            process_written = RawDecoding.write_data_to_nc(data_dict=bs_raw_decode, grp_process=grp_process)

            ds_raw.close()

            if process_written is False:
                raise RuntimeError("Error occurred writing to file!")

            attributes_written = params_raw_decode.nc_write_parameters(grp_process=grp_process)
            if attributes_written is False:
                raise RuntimeError("Error occured writing to file!")

            # store and update nc files
            process_logged = self.store_process(nc=ds_process, process_string=nc_process_name)
            if process_logged is False:
                raise RuntimeError("Error updating process string")

            return True

    def static_gain_correction(self, process_file_path: Path, raw_path: Path, parameters: Parameters):
        # create nc objects
        ds_process = Dataset(filename=process_file_path, mode='a')
        ds_raw = Dataset(filename=raw_path, mode='a')

        params_static_gain = parameters.static_gains

        #check process has not been calculated before
        process_name_str = params_static_gain.process_hash()
        has_been_processed = self.check_raw_process(nc_process=ds_process, process_string=process_name_str)
        if has_been_processed is True:
            logger.debug("Processing step has been computed prior")



