import glob
import logging
import os

from netCDF4 import Dataset
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.parameters import Parameters
from hyo2.openbst.lib.processing.process_management.process_manager import ProcessManager
from hyo2.openbst.lib.processing.process_methods.dicts import ProcessMethods
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecoding
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainCorrection

logger = logging.getLogger(__name__)


class Process:
    ext = ".nc"

    def __init__(self, process_path: Path) -> None:
        self._path = process_path
        self.proc_manager = ProcessManager()


    @property
    def path(self) -> Path:
        return self._path

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

        # if process_string.split('__')[0] == '00':
        #     self.step = 0
        # else:
        #     self.step += 1
        # self.parent_process = process_string
        return True

    def run_process(self, process_type: ProcessMethods, process_file_path: Path, raw_path: Path, parameters: Parameters):
        # Create the nc objects for reading
        ds_process = Dataset(filename=process_file_path, mode='r')
        ds_raw = Dataset(filename=raw_path, mode='r')

        # Grab the appropriate parameters object for the task
        params_object = parameters.get_process_params(process_type=process_type)

        # Check processing chain history for repeats and requirements
        has_been_processed = self.proc_manager.start_process(nc_process=ds_process, parameter_object=parameters)
        if has_been_processed is True:
            return True
