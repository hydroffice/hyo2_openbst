import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Optional

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceParams
logger = logging.getLogger(__name__)


# ## Area correction enum and dictionaries ##
class AreaCorrectionEnum(Enum):
    flat_seafloor = 0
    local_slope = 1


area_correction_title = {
    AreaCorrectionEnum.flat_seafloor: "Corrected Backscatter - Area Correction Using Flat Sealoor Assumption",
    AreaCorrectionEnum.local_slope: "Corrected Backscatter - Area Correction Using Local Slope"
}


# ## Area Correction Parameters Object ##
class AreaCorrectionParameters:
    process_name = "area_correction"

    def __init__(self):
        self.method_type = AreaCorrectionEnum.flat_seafloor

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = area_correction_title[self.method_type]
            grp_process.method_type = self.method_type.name
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


# ## Area Compensation Class and Methods ##
class AreaCompensation:

    def __init__(self):
        pass

    @classmethod
    def area_correction(cls, ds_process: Dataset, ds_raw: Dataset,
                        parent: str, parameters: AreaCorrectionParameters):

        p_method_type = parameters.method_type

        grp_beam_geo = ds_raw.groups['beam_geometry']
        var_rx_bw_across = grp_beam_geo.variables['across_beamwidth']
        data_rx_bw_across = var_rx_bw_across[:]

        grp_runtime = ds_raw.groups['runtime_settings']
        var_tx_bw_along = grp_runtime.variables['tx_along_beam_width']
        data_tx_be_along = var_tx_bw_along[:]
        var_sound_speed = grp_runtime.variables['sound_velocity']
        data_sound_speed = var_sound_speed[:]
        var_pulse_length = grp_runtime.variables['tx_pulse_width']
        data_pulse_length = var_pulse_length[:]

        grp_raw = ds_raw.groups['raw_bathymetry_data']
        var_rx_angle = grp_raw.variables['rx_angle']
        data_rx_angle = var_rx_angle[:]

        data_backscatter = cls.find_bs_data(ds_process=ds_process, parent=parent)
        data_raypath = cls.find_ray_data(ds_process=ds_process, parent=parent)

        if data_backscatter is None:
            logger.error("Step not computed: Backscatter data not found")
            return False

        if data_raypath is None:
            logger.error("Step not computed: Raypath data not found")
            return False

        if p_method_type is AreaCorrectionEnum.flat_seafloor:
            data_out = cls.flat_seafloor(backscatter=data_backscatter,
                                         rx_angle=data_rx_angle, raypath=data_raypath,
                                         rx_beamwidth_across=data_rx_bw_across,
                                         tx_beamwidth_along=data_tx_be_along[:, np.newaxis],
                                         pulse_len=data_pulse_length[:, np.newaxis],
                                         sound_speed=data_sound_speed[:, np.newaxis])

        elif p_method_type is AreaCorrectionEnum.local_slope:
            data_out = None
            pass
        else:
            raise TypeError("Urecognized Method Type: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        try:
            grp_process.createDimension(dimname='ping', size=None)
            grp_process.createDimension(dimname='beam', size=None)
            grp_process.createDimension(dimname='angle', size=None)

            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_bs_data[:] = data

                elif data_name == 'area_correction':
                    var_area_corr = grp_process.createVariable(varname='area_correction',
                                                               datatype='f8',
                                                               dimensions=('ping', 'beam'))
                    var_area_corr[:] = data

                elif data_name == 'area_corr_beam_limited':
                    var_area_bl = grp_process.createVariable(varname='beam_limited_area_correction',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_area_bl[:] = data
                elif data_name == 'area_corr_pulse_limited':
                    var_area_pl = grp_process.createVariable(varname='pulse_limited_area_correction',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_area_pl[:] = data

            return True
        except RuntimeError:
            return False

    @classmethod
    def flat_seafloor(cls,
                      backscatter: np.ma.MaskedArray, rx_angle: np.ma.MaskedArray, raypath: np.ma.MaskedArray,
                      rx_beamwidth_across: np.ndarray, tx_beamwidth_along: np.ndarray,
                      pulse_len: np.ndarray, sound_speed: np.ndarray):

        rx_beamwidth_across = np.deg2rad(rx_beamwidth_across)
        tx_beamwidth_along = np.deg2rad(tx_beamwidth_along)
        rx_angle = np.deg2rad(rx_angle)

        area_beam_lim = rx_beamwidth_across * tx_beamwidth_along * raypath ** 2
        area_pulse_lim = ((sound_speed * pulse_len) / (2 * np.sin(np.abs(rx_angle)))) * (tx_beamwidth_along * raypath)

        area_correction = 10 * np.ma.log10(np.minimum(area_beam_lim, area_pulse_lim))

        bs_corrected = backscatter - area_correction

        data_out = {
            'backscatter_data': bs_corrected,
            'area_correction': area_correction,
            'area_corr_beam_limited': 10 * np.ma.log10(area_beam_lim),
            'area_corr_pulse_limited': 10 * np.ma.log10(area_pulse_lim)
        }

        return data_out

    @classmethod
    def local_slope(cls):
        pass

    @classmethod
    def find_bs_data(cls, ds_process: Dataset, parent: str):
        grp_parent = ds_process.groups[parent]
        try:
            var_backscatter = grp_parent.variables['backscatter_data']
            data_backscatter = var_backscatter[:]
            return data_backscatter
        except KeyError:
            parent = grp_parent.parent_process
            if parent == 'ROOT':
                return None

            data_backscatter = cls.find_bs_data(ds_process=ds_process, parent=parent)
            return data_backscatter

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

