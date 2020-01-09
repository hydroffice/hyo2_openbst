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
            logger.debug("Something went wrong writing attributes")

    def process_hash(self) -> str:
        process_string = StaticGainParameters.process_name + '__'
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        hash_string = process_string + NetCDFHelper.hash_string(parameter_string)
        return hash_string


class StaticGainCorrection:

    def __init__(self):
        pass

    @classmethod
    def static_correction(cls,ds_process: Dataset, parameters: StaticGainParameters,) -> dict:
        p_method_type = parameters.method_type

        if p_method_type is StaticGainEnum.gain_removal:
            pass
        elif p_method_type is StaticGainEnum.gain_addition:
            pass
        else:
            raise TypeError("Unrecognized Satic Gain Correction Method: ")

        data_out = {
            # 'backscatter_data': bs_static_gain_corrected
        }
        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        try:
            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    dim_ping = grp_process.createDimension(dimname='ping', size=None)
                    dim_beam = grp_process.createDimension(dimname='beam', size=None)
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_bs_data[:] = data

                return True
        except RuntimeError:
            logger.debug("Something went wrong writing data to nc file")
            return False

    # ## Processing Methods ##
    @classmethod
    def added_gain(cls):
        pass

    @classmethod
    def subtracted_gain(cls):
        pass



