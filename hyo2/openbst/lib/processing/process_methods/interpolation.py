import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Union
from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Interpolation Enum and Dictionaries ##
class InterpEnum(Enum):
    simple = 0


interpolation_title = {
    InterpEnum.simple: "Interpolated Motion Data"
}


# ## Interpolation Parameter Object ##
class InterpParameters:
    process_name = "motion_interpolation"

    def __init__(self):
        self.method_type = InterpEnum.simple

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = interpolation_title[self.method_type]
            grp_process.method_type = self.method_type.name
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = InterpParameters.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids

# ## Interpolation Class and Methods ##
class Interpolation:

    def __init__(self):
        pass

    @classmethod
    def interpolate(cls):
        pass

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        pass

    # Processing Method Types #
    @classmethod
    def simple(cls):
        pass
