import glob
import logging
import os

from enum import Enum
from netCDF4 import Dataset
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.parameters import Parameters
from hyo2.openbst.lib.processing.raw_decoding import RawDecoding

logger = logging.getLogger(__name__)


class ProcessStageStatus(Enum):
    # Already in processing chain
    PRIORPROCESS = 0
    REPEATEPROCESS = 1

    # Not in processing chain
    NEWPROCESS = 2
    MODIFIEDPROCESS = 3


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
    def parent_process(self) -> str:
        return self._prior_process

    @parent_process.setter
    def parent_process(self, current_process):
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

        if process_string.split('__')[0] == '00':
            self.step = 0
        else:
            self.step += 1

        self.parent_process = process_string
        return True

    def check_process(self, nc_process: Dataset, process_string: str) -> ProcessStageStatus:
        process_identifiers = process_string.split('__')
        parent_identifiers = self.parent_process.split('__')

        # Check if this is the first process
        if self.parent_process == '':
            return ProcessStageStatus.NEWPROCESS

        # Check new process against parent process
        if process_identifiers[0] == parent_identifiers[1]:
            if process_identifiers[-1] == parent_identifiers[-1]:
                return ProcessStageStatus.PRIORPROCESS
            else:
                return ProcessStageStatus.MODIFIEDPROCESS
        else:
            # Check if step has been computed prior in chain
            in_process_chain = self.check_process_chain(nc_process=nc_process,
                                                        process_str=process_string,
                                                        parent_str=self.parent_process)

    @staticmethod
    def check_process_chain(nc_process: Dataset, process_str: str, parent_str: str) -> bool:
        process_identifiers = process_str.split('__')
        # Find grp_process that matches current parent
        grp_prior = nc_process.groups[parent_str]
        nc_parent_str = grp_prior.parent_process
        nc_parent_identifiers = nc_parent_str.split('__')
        if nc_parent_identifiers[1] == '':
            return False
        elif nc_parent_identifiers[1] == process_identifiers[1]:
            return True
        else:
            Process.check_process_chain(nc_process=nc_process, process_str=process_str, parent_str=nc_parent_str)


        # Grab parent

        # Compare parents

        # if not same recursive call

    # ## Processing Methods ##
    def raw_decode(self, process_file_path: Path, raw_path: Path, parameters: Parameters):
        # create nc objects
        ds_process = Dataset(filename=process_file_path, mode='a')
        ds_raw = Dataset(filename=raw_path, mode='a')

        params_raw_decode = parameters.rawdecode

        # check process has not been calculated before
        process_name_str = params_raw_decode.process_hash()
        has_been_processd = self.check_process(nc_process=ds_process, process_string=process_name_str)

        if has_been_processd == ProcessStageStatus.PRIORPROCESS:
            logger.debug("Processing step has been computed prior")
            return True
        else:

            bs_raw_decode = RawDecoding.decode(ds_raw=ds_raw, parameters=params_raw_decode)

            # Write data to nc file
            initial_step = 0
            nc_process_name = "%02d" % initial_step + '__' + process_name_str
            grp_process = ds_process.createGroup(nc_process_name)
            grp_process.parent_process = ''
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

        # check process has not been calculated before
        process_name_str = params_static_gain.process_hash()
        has_been_processed = self.check_process(nc_process=ds_process, process_string=process_name_str)
        if has_been_processed is True:
            logger.debug("Processing step has been computed prior")
