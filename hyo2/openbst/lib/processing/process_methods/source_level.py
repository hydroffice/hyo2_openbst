import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Source Level Enum and Dictionaries ##
class SourceLevelEnum(Enum):
    gain_removal = 0
    gain_addition = 1


source_level_title = {
    SourceLevelEnum.gain_removal: "Correceted Backscatter - Source Level Subtracted",
    SourceLevelEnum.gain_addition: " Corrected Backscatter - Source Level Subtracted"
}


# ## Source Level Correction Parameters Object
class SourceLevelParameters:
    process_name = "source_level_compensation"

    def __init__(self):
        self.method_type = SourceLevelEnum.gain_removal

    def nc_write_parameters(self, grp_process: Group):
        try:
            for method_enum in SourceLevelEnum:
                if self.method_type == method_enum:
                    grp_process.title = source_level_title[method_enum]
                    grp_process.method_type = method_enum.name
                    break
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = SourceLevelParameters.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


class SourceLevel:

    def __init__(self):
        pass

    @classmethod
    def source_level_correction(cls, ds_process: Dataset, ds_raw: Dataset,
                                parent: str, parameters: SourceLevelParameters):
        p_method_type = parameters.method_type
        grp_runtime = ds_raw.groups['runtime_settings']
        var_source_level = grp_runtime.variables['source_level']
        data_source_level = var_source_level[:]
        data_source_level = data_source_level[:, np.newaxis]
        grp_parent = ds_process.groups[parent]
        var_backscatter = grp_parent.variables['backscatter_data']
        data_backscatter = var_backscatter[:]

        if p_method_type is SourceLevelEnum.gain_removal:
            data_out = SourceLevel.subtract_gain(source_level=data_source_level, backscatter=data_backscatter)
        elif p_method_type is SourceLevelEnum.gain_addition:
            data_out = SourceLevel.add_gain(source_level=data_source_level, backscatter=data_backscatter)
        else:
            raise TypeError("Unrecognized Source Level Gain Correction Method: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls,data_dict: dict, grp_process: Group):
        try:
            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    grp_process.createDimension(dimname='ping', size=None)
                    grp_process.createDimension(dimname='beam', size=None)
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_bs_data[:] = data
            return True
        except RuntimeError:
            return False

    @classmethod
    def subtract_gain(cls, source_level: np.ma.MaskedArray, backscatter: np.ma.MaskedArray):
        bs_corrected = backscatter - source_level

        # Create the output data dictionary
        data_out = {
            'backscatter_data': bs_corrected
        }
        return data_out

    @classmethod
    def add_gain(cls, source_level: np.ma.MaskedArray, backscatter: np.ma.MaskedArray):
        bs_corrected = backscatter + source_level

        # Create the output data dictionary
        data_out = {
            'backscatter_data': bs_corrected
        }
        return data_out
