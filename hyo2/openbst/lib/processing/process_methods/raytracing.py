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

    def process_identifiers(self):
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
        data_sensor_soundspeed = data_sensor_soundspeed[:, np.newaxis]

        grp_bathy = ds_raw.groups['raw_bathymetry_data']
        var_sample_rate = grp_bathy.variables['sample_rate']
        data_sample_rate = var_sample_rate[:]
        data_sample_rate = data_sample_rate[:, np.newaxis]
        var_detect_point = grp_bathy.variables['detect_point']
        data_detect_point = var_detect_point[:]

        if p_method_type is RayTraceEnum.slant_range_approximation:
            # TODO: Assuming that sometime there is no surface ss probe, what do we use and how do we check
            data_out = cls.slant_range(detection_point=data_detect_point,
                                       surface_sound_speed=data_sensor_soundspeed,
                                       sample_rate=data_sample_rate)

        elif p_method_type is RayTraceEnum.using_ssp:
            # TODO: Figure out a way to reference the motion compensation so I can actually do ssp calculations
            grp_motion = ds_process.groups['PLACEHOLDER']
            data_out = None
        else:
            raise TypeError("Unrecognized Raytrace Method Type: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls,data_dict: dict, grp_process: Group):
        try:
            for data_name, data in data_dict.items():
                if data_name == 'ray_path_length':
                    grp_process.createDimension(dimname='ping', size=None)
                    grp_process.createDimension(dimname='beam', size=None)
                    var_range_data = grp_process.createVariable(varname='path_length',
                                                                datatype='f8',
                                                                dimensions=('ping', 'beam'))
                    var_range_data.longname = "computed_ray_path_length"
                    var_range_data.units = 'm'
                    var_range_data[:] = data

            return True
        except RuntimeError:
            return False

    @classmethod
    def slant_range(cls,
                    detection_point: np.ma.MaskedArray,
                    surface_sound_speed: np.ma.MaskedArray,
                    sample_rate: np.ma.MaskedArray):

        ray_path_length = detection_point / sample_rate * surface_sound_speed / 2
        data_out = {
            'ray_path_length': ray_path_length
        }
        return data_out

    @classmethod
    def using_ssp(cls):
        pass
