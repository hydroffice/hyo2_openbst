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
    InterpEnum.simple: "Interpolated Motion Datat"
}


# ## Interpolation Parameter Object ##
class InterpParameters:
    process_name = "motion_interpolation"

    def __init__(self):
        self.method_type = InterpEnum.simple
        
    def nc_write_parameters(self, grp_process: Group):
        pass

    def process_identifiers(self) -> list:
        pass


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
