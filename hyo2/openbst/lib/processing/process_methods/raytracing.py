import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Raytrace Enum and dicts
class RayTraceEnum(Enum):
    slant_range_approximation = 0
    using_ssp = 1


ray_trace_title = {
    RayTraceEnum.slant_range_approximation: "Raytracing - Slant Range Approximation",
    RayTraceEnum.using_ssp: "Raytracing - Using Sound Speed Profile"
}


# ## Raytracing Parameter Object ##
class RayTraceParams:
    process_name = "ray_tracing"

    def __init__(self):
        self.method_type = RayTraceEnum.slant_range_approximation
        self.default_surface_sound_speed = 1500

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = ray_trace_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.default_sensor_sound_speed = self.default_surface_sound_speed
            return True

        except TypeError:
            return False

    def process_identifier(self):
        process_string = RayTraceParams.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids

class RayTrace:

    def __init__(self):
        pass

    @classmethod
    def ray_trace(cls, ds_process: Dataset, ds_raw: Dataset,
                  parent: str, parameters: RayTraceParams):
        p_method_type = parameters.method_type

        grp_runtime = ds_raw.groups['runtime_settings']
        var_sensor_soundspeed = grp_runtime.variables['sound_velocity']
        data_sensor_soundspeed = var_sensor_soundspeed[:]

        if p_method_type is RayTraceEnum.slant_range_approximation:
            pass
        elif p_method_type is RayTraceEnum.using_ssp:
            pass
        else:
            raise TypeError("Unrecognized Raytrace Method Type: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls,data_dict: dict, grp_process: Group):
        pass

    @classmethod
    def slant_range(cls):
        pass

    @classmethod
    def using_ssp(cls):
        pass
