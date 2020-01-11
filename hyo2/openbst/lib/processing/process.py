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

    def run_process(self, process_method: ProcessMethods, process_file_path: Path, raw_path: Path,
                    parameters: Parameters):
        # Create the nc objects for reading
        ds_process = Dataset(filename=process_file_path, mode='r')
        ds_raw = Dataset(filename=raw_path, mode='r')

        # Check processing chain history for repeats and requirements
        do_process = self.proc_manager.start_process(process_type=process_method,
                                                     nc_process=ds_process,
                                                     parameter_object=parameters)
        if do_process is True:
            return True

        # Run the process
        method_parameters = parameters.get_process_params(process_type=process_method)
        if process_method == ProcessMethods.RAWDECODE:
            data_out = RawDecoding.decode(ds_raw=ds_raw, parameters=method_parameters)
        elif process_method == ProcessMethods.STATICGAIN:
            data_out = StaticGainCorrection.static_correction(ds_process=ds_process,
                                                              ds_raw=ds_raw,
                                                              parent=self.proc_manager.parent_process,
                                                              parameters=method_parameters)
        else:
            raise RuntimeError("We realistically cannot get to this point as there is no error handling in the above"
                               "method calls")

        ds_process.close()
        ds_raw.close()

        # Store the process
        process_written = self.store_process(process_method=process_method,
                                             nc_process_file=process_file_path,
                                             parameters=method_parameters,
                                             data=data_out)

        return True

    def store_process(self, process_method: ProcessMethods, nc_process_file: Path, parameters, data: dict) -> bool:
        ds_process = Dataset(filename=nc_process_file, mode='a')

        # create new group
        grp_process = ds_process.createGroup(self.proc_manager.current_process)

        # Store the parameters as group attributes
        attributes_written = parameters.nc_write_parameters(grp_process=grp_process)
        if attributes_written is False:
            raise RuntimeError("Something went wrong writing attributes")

        # Store the process
        if process_method == ProcessMethods.RAWDECODE:
            process_written = RawDecoding.write_data_to_nc(data_dict=data, grp_process=grp_process)
        elif process_method == ProcessMethods.STATICGAIN:
            process_written = StaticGainCorrection.write_data_to_nc(data_dict=data, grp_process=grp_process)
        else:
            raise RuntimeError("Unrecognized processing method type: %s" % process_method)

        if process_written is False:
            raise RuntimeError("Something went wrong writing data")

        NetCDFHelper.update_modified(ds=ds_process)
        ds_process.close()
        self.proc_manager.update_process()

        return True
