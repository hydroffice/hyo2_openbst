import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group
from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Interpolation Enum and Dictionaries ##
class InterpEnum(Enum):
    simple_linear = 0


interpolation_title = {
    InterpEnum.simple_linear: "Interpolated Motion Data"
}


# ## Interpolation Parameter Object ##
class InterpParameters:
    process_name = "motion_interpolation"

    def __init__(self):
        self.method_type = InterpEnum.simple_linear

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
    def interpolate(cls, ds_raw: Dataset,
                    parameters: InterpParameters) -> dict:
        p_method_type = parameters.method_type

        grp_position = ds_raw.groups['position']
        var_pos_time = grp_position.variables['time']
        data_pos_time = var_pos_time[:]
        var_latitude = grp_position.variables['latitude']
        data_latitude = var_latitude[:]
        var_longitude = grp_position.variables['longitude']
        data_longitude = var_longitude[:]

        grp_attitude = ds_raw.groups['attitude']
        var_motion_time = grp_attitude.variables['time']
        data_motion_time = var_motion_time[:]
        var_pitch = grp_attitude.variables['pitch']
        data_pitch = var_pitch[:]
        var_roll = grp_attitude.variables['roll']
        data_roll = var_roll[:]
        var_heave = grp_attitude.variables['heave']
        data_heave = var_heave[:]
        var_heading_time = grp_attitude.variables['heading_time']
        data_heading_time = var_heading_time[:]
        var_heading = grp_attitude.variables['heading']
        data_heading = var_heading[:]

        grp_snippets = ds_raw.groups['snippets']
        var_snippet_time = grp_snippets.variables['time']
        data_snippet_time = var_snippet_time[:]

        if p_method_type is InterpEnum.simple_linear:
            data_out = cls.simple_linear(ping_time=data_snippet_time,
                                         position_time=data_pos_time, latitude=data_latitude,
                                         longitude=data_longitude,
                                         attitude_time=data_motion_time, pitch=data_pitch, roll=data_roll,
                                         heave=data_heave,
                                         heading_time=data_heading_time, heading=data_heading)

        else:
            raise TypeError("Unrecognized Interpolation Method: %s", p_method_type)

        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        try:
            grp_process.createDimension(dimname='time', size=None)
            for data_name, data in data_dict.items():
                if data_name == 'time':
                    var_time = grp_process.createVariable(varname=data_name,
                                                          datatype='f8',
                                                          dimensions=('time',))
                    var_time[:] = data
                elif data_name == 'latitude':
                    var_latitude = grp_process.createVariable(varname=data_name,
                                                              datatype='f8',
                                                              dimensions=('time',))
                    var_latitude[:] = data
                elif data_name == 'longitude':
                    var_longitude = grp_process.createVariable(varname=data_name,
                                                               datatype='f8',
                                                               dimensions=('time',))
                    var_longitude[:] = data
                elif data_name == 'roll':
                    var_roll = grp_process.createVariable(varname=data_name,
                                                          datatype='f8',
                                                          dimensions=('time',))
                    var_roll[:] = data
                elif data_name == 'pitch':
                    var_pitch = grp_process.createVariable(varname=data_name,
                                                           datatype='f8',
                                                           dimensions=('time',))
                    var_pitch[:] = data
                elif data_name == 'heave':
                    var_heave = grp_process.createVariable(varname=data_name,
                                                           datatype='f8',
                                                           dimensions=('time',))
                    var_heave[:] = data
                elif data_name == 'yaw':
                    var_yaw = grp_process.createVariable(varname=data_name,
                                                         datatype='f8',
                                                         dimensions=('time',))
                    var_yaw[:] = data
                else:
                    continue
            return True
        except RuntimeError:
            return False

    # Processing Method Types #
    @classmethod
    def simple_linear(cls,
                      ping_time: np.ndarray,
                      position_time: np.ndarray, latitude: np.ndarray, longitude: np.ndarray,
                      attitude_time: np.ndarray, pitch: np.ndarray, roll: np.ndarray, heave: np.ndarray,
                      heading_time: np.ndarray, heading: np.ndarray):
        """Simple linear interpolation, if any pings times fall outside the motion timeseries, they are set to NAN"""

        # Position
        lat_interp = np.interp(ping_time, position_time, latitude, left=np.nan, right=np.nan)
        lon_interp = np.interp(ping_time, position_time, longitude, left=np.nan, right=np.nan)

        # Attitude
        roll_interp = np.interp(ping_time, attitude_time, roll, left=np.nan, right=np.nan)
        pitch_interp = np.interp(ping_time, attitude_time, pitch, left=np.nan, right=np.nan)
        heave_interp = np.interp(ping_time, attitude_time, heave, left=np.nan, right=np.nan)
        yaw_interp = np.interp(ping_time, heading_time, heading, left=np.nan, right=np.nan)

        data_out = {
            'time': ping_time,
            'latitude': lat_interp,
            'longitude': lon_interp,
            'roll': roll_interp,
            'pitch': pitch_interp,
            'heave': heave_interp,
            'yaw': yaw_interp
        }
        return data_out



