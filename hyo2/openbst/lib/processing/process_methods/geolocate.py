import logging
import numpy as np
import utm

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Optional

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.process_methods.interpolation import InterpParameters
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceParams

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
    def geolocate(cls, ds_process: Dataset, ds_raw: Dataset,
                  parent: str, parameters: GeolocateParameters):

        p_method_type = parameters.method_type
        p_prj = parameters.prj
        p_geoid = parameters.geoid

        grp_raw_bathy = ds_raw.groups['raw_bathymetry_data']
        var_rx_angle = grp_raw_bathy.variables['rx_angle']
        data_rx_angle = var_rx_angle[:]

        grp_interp = cls.find_interp_data(ds_process=ds_process, parent=parent)
        var_lat = grp_interp.variables['latitude']
        var_lon = grp_interp.variables['longitude']
        var_yaw = grp_interp.variables['yaw']
        data_lat = var_lat[:]
        data_lon = var_lon[:]
        data_yaw = var_yaw[:]
        data_yaw = data_yaw[:, np.newaxis]

        data_raypath = cls.find_ray_data(ds_process=ds_process, parent=parent)

        if grp_interp is None:
            logger.error("Step not computed: Interpolated data not found")
            return False

        if data_raypath is None:
            logger.error("Step not computed: Raypath data not found")
            return False

        if p_method_type is GeolocateEnum.simple:

            data_out = cls.simple(raypath=data_raypath, rx_angle=data_rx_angle,
                                  lat=data_lat, lon=data_lon, yaw=data_yaw,
                                  geoid=p_geoid, projection=p_prj)
            pass
        elif p_method_type is GeolocateEnum.motion_comp:
            data_out = None
            pass
        else:
            raise TypeError("Unrecognized Method Type: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        try:
            grp_process.createDimension(dimname='ping', size=None)
            grp_process.createDimension(dimname='beam', size=None)
            crs = grp_process.createVariable(varname='crs',
                                             datatype='i4', dimensions=())

            for data_name, data in data_dict.items():
                if data_name == 'geoid':
                    crs.geoid = data

                elif data_name == 'projection':
                    crs.projection = data

                elif data_name == 'latitude':
                    var_lat = grp_process.createVariable(varname='latitude',
                                                         datatype='f8',
                                                         dimensions=('ping', 'beam'))
                    var_lat[:] = data
                    var_lat.units = 'degrees_east'
                    var_lat.long_name = 'latitude'

                elif data_name == 'longitude':
                    var_lon = grp_process.createVariable(varname='longitude',
                                                         datatype='f8',
                                                         dimensions=('ping', 'beam'))
                    var_lon[:] = data
                    var_lon.units = 'degrees_north'
                    var_lon.long_name = 'longitude'

                elif data_name == 'depth':
                    var_depth = grp_process.createVariable(varname='depth',
                                                           datatype='f8',
                                                           dimensions=('ping', 'beam'))
                    var_depth[:] = data
                    var_depth.long_name = 'depth_below_sonar'
                    var_depth.units = 'm'
                elif data_name == 'eastings':
                    var_east = grp_process.createVariable(varname='eastings',
                                                          datatype='f8',
                                                          dimensions=('ping', 'beam'))
                    var_east.long_name = 'eastings'
                    var_east.units = 'm'

                elif data_name == 'northings':
                    var_north = grp_process.createVariable(varname='northings',
                                                           datatype='f8',
                                                           dimensions=('ping', 'beam'))
                    var_north.long_name = 'northings'
                    var_north.units = 'm'

                elif data_name == 'zone_number':
                    crs.zone_number = data

                elif data_name == 'zone_letter':
                    crs.zone_letter = data

            return True
        except RuntimeError:
            return False

    @classmethod
    def simple(cls,
               raypath: np.ma.MaskedArray,
               rx_angle: np.ma.MaskedArray,
               lat: np.ndarray, lon: np.ndarray,
               yaw: np.ma.MaskedArray,
               geoid: str, projection: str):

        num_pings, num_beams = rx_angle.shape
        rx_angle = np.deg2rad(rx_angle.filled(fill_value=np.nan))
        raypath = raypath.filled(fill_value=np.nan)
        yaw = np.deg2rad(yaw)

        # - Determine the easting and northing of each ping
        zn_num = None
        zn_letter = None
        ee_ping = np.zeros(shape=lon.shape)
        nn_ping = np.zeros(shape=lat.shape)

        for ping in range(num_pings):
            ee_ping[ping], nn_ping[ping], zn_num, zn_letter = utm.from_latlon(lat[ping], lon[ping])

        # - Determine x,y,z in ship reference frame
        # TODO: use proper georefencing
        y_shiprf = raypath * np.sin(rx_angle)  # Negative rx angles are portside
        x_shiprf = np.zeros(y_shiprf.shape)  # Assume no forward displacement
        z_shiprf = raypath * np.cos(rx_angle)

        # - Determine x,y,z in geographic reference frame (meters) relative to ship
        x_georf = np.ones((num_pings, num_beams)) * np.nan
        y_georf = x_georf.copy()

        for ping in range(num_pings):
            y = y_shiprf[ping, :]
            x = x_shiprf[ping, :]
            rot_matrix = np.asarray([[np.cos(yaw[ping]), -np.sin(yaw[ping])], [np.sin(yaw[ping]), np.cos(yaw[ping])]])
            x_georf[ping, :], y_georf[ping, :] = rot_matrix.squeeze() @ np.asarray([x, y])

        ee_sounding = y_georf + ee_ping[:, np.newaxis]
        nn_sounding = x_georf + nn_ping[:, np.newaxis]

        if projection == 'Geographic':
            lon_sounding = np.ones(shape=rx_angle.shape) * np.nan
            lat_sounding = lon_sounding.copy()

            for ping in range(num_pings):
                for beam in range(num_beams):
                    if np.isnan(ee_sounding[ping, beam]):
                        continue

                    lon_sounding[ping, beam], lat_sounding[ping, beam] = utm.to_latlon(ee_sounding[ping, beam],
                                                                                       nn_sounding[ping, beam],
                                                                                       zone_number=zn_num,
                                                                                       zone_letter=zn_letter)

            data_out = {
                'geoid': geoid,
                'projection': projection,
                'latitude': lat_sounding,
                'longitude': lon_sounding,
                'depth': z_shiprf
            }
        elif projection == 'UTM':
            data_out = {
                'geoid': geoid,
                'projection': projection,
                'zone_letter': zn_letter,
                'zone_number': zn_num,
                'eastings': ee_sounding,
                'northings': nn_sounding,
                'depth': z_shiprf,
            }
        return data_out

    @classmethod
    def motion_comp(cls):
        pass

    # helper functions
    # TODO: These helper functions should be placed in a different module, likely nchelper, so we don't repeate code
    @classmethod
    def find_interp_data(cls, ds_process: Dataset, parent: str):
        grp_parent = ds_process.groups[parent]

        if InterpParameters.process_name in parent:
            return grp_parent

        elif grp_parent.parent_process == 'ROOT':
            return None

        else:
            parent = grp_parent.parent_process
            grp_parent = cls.find_interp_data(ds_process=ds_process, parent=parent)
            return grp_parent

    @classmethod
    def find_ray_data(cls, ds_process: Dataset, parent: str):
        grp_parent = ds_process.groups[parent]

        if RayTraceParams.process_name in parent:
            var_ray_path = grp_parent.variables['path_length']
            data_ray_path = var_ray_path[:]
            return data_ray_path

        elif grp_parent.parent_process == 'ROOT':
            return None

        else:
            parent = grp_parent.parent_process
            data_ray_path = cls.find_ray_data(ds_process=ds_process, parent=parent)
            return data_ray_path
