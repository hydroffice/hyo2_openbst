import logging
import numpy as np
import utm

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Optional

from hyo2.openbst.lib.nc_helper import NetCDFHelper


logger = logging.getLogger(__name__)


# ## Geolocation Enum and dictionaries ##
class GeolocateEnum(Enum):
    simple = 0
    motion_comp = 1


geolocate_title = {
    GeolocateEnum.simple: "Geolocated Data - Simple Projection",
    GeolocateEnum.motion_comp: "Geolocated Data - Fully Georeferenced"
}


# ## Geolocation Parameters Object ##
class GeolocateParameters:
    process_name = "geolocation"

    def __init__(self):
        self.method_type = GeolocateEnum.simple
        self.geoid = 'WGS84'
        self.prj = 'Geographic'

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = geolocate_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.geoid = self.geoid
            grp_process.projection = self.prj
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = self.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


# Geolocation class and methods
class Geolocation:

    def __init__(self):
        pass

    @classmethod
    def geolocation(cls,ds_process: Dataset, ds_raw: Dataset,
                    parent: str, parameters: GeolocateParameters):

        p_method_type = parameters.method_type
        p_prj = parameters.prj
        p_geoid = parameters.geoid

        if p_method_type is GeolocateEnum.simple:
            pass
        elif p_method_type is GeolocateEnum.motion_comp:
            pass
        else:
            raise TypeError("Unrecognized Method Type: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        pass

    @classmethod
    def simple(cls):
        pass

    @classmethod
    def motion_comp(cls):
        pass