import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group

from hyo2.openbst.lib.nc_helper import NetCDFHelper
logger = logging.getLogger(__name__)


# ## Static Gain Compensation Enum and Dictionaries ##
class StaticGainEnum(Enum):
    gain_removal = 0
    gain_addition = 1


static_gain_title = {
    StaticGainEnum.gain_removal: "Corrected Backscatter - Static Gain Removed",
    StaticGainEnum.gain_addition: "Corrected Backscatter - Static Gain Added"
}


# ## Static Gain Correction Parameter Object ##
class StaticGainParameters:
    process_name = "static_gain_compensation"

    def __init__(self):
        self.method_type = StaticGainEnum.gain_removal

    def nc_write_parameters(self, grp_process: Group):
        try:
            for method_enum in StaticGainEnum:
                if self.method_type == method_enum:
                    grp_process.title = static_gain_title[method_enum]
                    grp_process.method_type = method_enum.name
                    break
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = StaticGainParameters.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


class StaticGainCorrection:

    def __init__(self):
        pass

    @classmethod
    def static_correction(cls, ds_process: Dataset, ds_raw: Dataset,
                          parent: str, parameters: StaticGainParameters) -> dict:
        p_method_type = parameters.method_type
        grp_runtime = ds_raw.groups['runtime_settings']      # TODO: Create dictionary in raws to reference.
        var_static_gain = grp_runtime.variables['static_gain']
        data_static_gain = var_static_gain[:]
        data_static_gain = data_static_gain[:, np.newaxis]
        grp_parent = ds_process.groups[parent]
        var_backscatter = grp_parent.variables['backscatter_data']
        data_backscatter = var_backscatter[:]

        if p_method_type is StaticGainEnum.gain_removal:
            data_out = StaticGainCorrection.subtracted_gain(static_gain=data_static_gain, backscatter=data_backscatter)
        elif p_method_type is StaticGainEnum.gain_addition:
            data_out = StaticGainCorrection.added_gain(static_gain=data_static_gain, backscatter=data_backscatter)
        else:
            raise TypeError("Unrecognized Static Gain Correction Method: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
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

    # ## Processing Methods ##
    @classmethod
    def added_gain(cls, static_gain: np.ma.MaskedArray, backscatter: np.ma.MaskedArray):
        bs_corrected = backscatter + static_gain

        # Create the output data dictionary
        data_out = {
            'backscatter_data': bs_corrected
        }
        return data_out

    @classmethod
    def subtracted_gain(cls, static_gain: np.ma.MaskedArray, backscatter: np.ma.MaskedArray):
        bs_corrected = backscatter - static_gain

        data_out = {
            'backscatter_data': bs_corrected
        }

        return data_out




