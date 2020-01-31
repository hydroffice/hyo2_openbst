import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Union
from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## TVG Gain Enum and Dictionaries ##
class TVGENUM(Enum):
    gain_removal_tvg_curve_from_manufacturer = 10
    gain_removal_tvg_curve_generated_from_gains = 11
    gain_removal_simple_tvg_curve = 12

    # gain_addition_tvg_curve_from_manaufacturer = 20
    # gain_addition_tvg_curve_generated_from_gains = 21
    # gain_addition_simple_tvg_curve = 22


tvg_gain_title = {
    TVGENUM.gain_removal_tvg_curve_from_manufacturer: "Corrected Backscatter - Manufacturer TVG Curve Subtracted",
    TVGENUM.gain_removal_tvg_curve_generated_from_gains: "Corrected Backscatter - TVG Curve from Runtime Settings "
                                                         "Subtracted",
    TVGENUM.gain_removal_simple_tvg_curve: "Corrected Backscatter - Simple TVG Curve Subtracted",
    # TVGENUM.gain_addition_tvg_curve_from_manaufacturer: "Corrected Backscatter - Manufacturer TVG Curve Added",
    # TVGENUM.gain_addition_tvg_curve_generated_from_gains: "Corrected Backscatter - TVG Curve from Runtime Settings "
    #                                                       "Added",
    # TVGENUM.gain_addition_simple_tvg_curve: "Corrected Backscatter - Simple TVG Curve Subtracted"
}


# ## TVG Gain Correction Parameter Object
class TVGCorrectionParameters:
    process_name = "tvg_correction"

    def __init__(self):
        self.method_type = TVGENUM.gain_removal_simple_tvg_curve
        self.user_spreading_gain = 30
        self.user_absorption_gain = 5

    def nc_write_parameters(self, grp_process: Group) -> bool:
        try:
            grp_process.title = tvg_gain_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.user_spreading_gain = self.user_spreading_gain
            grp_process.user_absorption_gain = self.user_absorption_gain
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = TVGCorrectionParameters.process_name
        parameter_string = str()
        for parameter, value in self.__dict__.items():
            parameter_string += parameter + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


# ## TVG class and methods ##
class TVG:

    def __init__(self):
        pass

    @classmethod
    def tvg_correction(cls, ds_process: Dataset, ds_raw: Dataset,
                       parent: str, parameters: TVGCorrectionParameters) -> Union[dict, bool]:
        p_method_type = parameters.method_type
        p_spreading = parameters.user_spreading_gain
        p_absorp = parameters.user_absorption_gain

        grp_parent = ds_process.groups[parent]
        var_backscatter = grp_parent.variables['backscatter_data']
        data_backscatter = var_backscatter[:]

        if p_method_type is TVGENUM.gain_removal_tvg_curve_from_manufacturer:
            try:
                grp_tvg = ds_raw.groups['time_varying_gain']
                var_tvg_curves = grp_tvg.variables['tvg_curves']
                data_tvg_curves = var_tvg_curves[:]
            except KeyError:
                logger.warning("Group: TVG and/or Variable: tvg_curves not found in raw .nc file")
                return False
            try:
                grp_snippet_data = ds_raw.groups['snippets']
                var_detection_point = grp_snippet_data.variables['detect_sample']
                data_detect_samples = var_detection_point[:]
                data_out = cls.remove_tvg_mfr_curve(tvg_curve_list=data_tvg_curves,
                                                    bottom_detection_point=data_detect_samples,
                                                    backscatter=data_backscatter)
            except KeyError:
                logger.warning("Group: snippets and/or Variable: detect_sample not found in raw .nc file")
                data_out = False

        elif p_method_type is TVGENUM.gain_removal_tvg_curve_generated_from_gains:
            grp_runtime = ds_raw.groups['runtime_settings']
            var_sample_rate = grp_runtime.variables['sample_rate']
            data_sample_rate = var_sample_rate[:]
            var_sound_velocity = grp_runtime.variables['sound_velocity']
            data_sound_speed = var_sound_velocity[:]
            var_spreading = grp_runtime.variables['spreading_gain']
            data_spreading = var_spreading[:]
            var_absorp_gain = grp_runtime.variables['absorption_gain']
            data_absorption = var_absorp_gain[:]

            try:
                grp_snippet_data = ds_raw.groups['snippets']
                var_detection_point = grp_snippet_data.variables['detect_sample']
                data_detect_samples = var_detection_point[:]
                data_out = cls.remove_tvg_mfr_gains(spreading=data_spreading,
                                                    alpha=data_absorption,
                                                    sample_rate=data_sample_rate,
                                                    bottom_detection_point=data_detect_samples,
                                                    sound_speed=data_sound_speed,
                                                    backscatter=data_backscatter)
            except KeyError:
                logger.warning("Group: snippets and/or Variable: detect_sample not found in raw .nc file")
                data_out = False

        elif p_method_type is TVGENUM.gain_removal_simple_tvg_curve:
            grp_runtime = ds_raw.groups['runtime_settings']
            var_sample_rate = grp_runtime.variables['sample_rate']
            data_sample_rate = var_sample_rate[:]
            var_sound_velocity = grp_runtime.variables['sound_velocity']
            data_sound_speed = var_sound_velocity[:]
            try:
                grp_snippet_data = ds_raw.groups['snippets']
                var_detection_point = grp_snippet_data.variables['detect_sample']
                data_detect_samples = var_detection_point[:]
                data_out = cls.remove_tvg_simple_curve(spreading=p_spreading,
                                                       alpha=p_absorp,
                                                       sample_rate=data_sample_rate,
                                                       bottom_detection_point=data_detect_samples,
                                                       sound_speed=data_sound_speed,
                                                       backscatter=data_backscatter)
            except KeyError:
                logger.warning("Group: snippets and/or Variable: detect_sample not found in raw .nc file")
                data_out = False
        else:
            raise TypeError("Unrecognized TVG Gain Correction Method: %s" % p_method_type)

        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        try:
            grp_process.createDimension(dimname='ping', size=None)
            grp_process.createDimension(dimname='beam', size=None)
            grp_process.createDimension(dimname='sample', size=None)

            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_bs_data[:] = data
                elif data_name == 'tvg_curves':
                    var_tvg_curves = grp_process.createVariable(varname='tvg_curves',
                                                                datatype='f8',
                                                                dimensions=('ping', 'sample'))
                    var_tvg_curves[:] = data
                elif data_name == 'tvg_beam_values':
                    var_tvg_values = grp_process.createVariable(varname='beam_tvg_value',
                                                                datatype='f8',
                                                                dimensions=('ping', 'beam'))
                    var_tvg_values[:] = data
                else:
                    continue
            return True
        except RuntimeError:
            return False

    # # Processing Method Types #
    @classmethod
    def remove_tvg_mfr_curve(cls, tvg_curve_list: np.ma.MaskedArray,
                             bottom_detection_point: np.ma.MaskedArray,
                             backscatter: np.ma.MaskedArray):

        numpings = backscatter.shape[0]
        numbeams = backscatter.shape[1]

        tvg_curve_matrix = np.ones(shape=(numpings, numbeams)) * np.nan
        for ping in range(numpings):
            beam_index = np.arange(numbeams, dtype='i8')
            beam_detection_sample = bottom_detection_point[ping, :]
            beam_mask = ~beam_detection_sample.mask
            beam_index = beam_index[beam_mask]
            beam_detection_sample = beam_detection_sample[beam_mask]

            ping_tvg_curve = tvg_curve_list[ping, :]
            tvg_value = ping_tvg_curve[beam_detection_sample]
            tvg_curve_matrix[ping, beam_index] = tvg_value

        bs_corrected = backscatter - np.ma.masked_invalid(tvg_curve_matrix)

        # Create the output data dictionary
        data_out = {
            'backscatter_data': bs_corrected,
            'tvg_curves': tvg_curve_list,
            'tvg_beam_values': tvg_curve_matrix
        }
        return data_out

    @classmethod
    def remove_tvg_mfr_gains(cls,
                             spreading: float,
                             alpha: float,
                             sample_rate: np.ndarray,
                             bottom_detection_point: np.ma.MaskedArray,
                             sound_speed: np.ndarray,
                             backscatter: np.ma.MaskedArray):

        sample_rate = sample_rate[:, np.newaxis]
        sound_speed = sound_speed[:, np.newaxis]
        spreading = spreading[:, np.newaxis]
        alpha = alpha[:,np.newaxis]
        range_m = bottom_detection_point / sample_rate * sound_speed / 2
        tvg_matrix = spreading * np.ma.log10(range_m) + 2 * (alpha / 1000) * range_m

        bs_corrected = backscatter - np.ma.masked_invalid(tvg_matrix)

        # Create an example tvg curve to store
        calc_max_range = np.ma.max(np.ma.max(range_m)) + 5
        calc_sample_range = calc_max_range * sample_rate * 2 / sound_speed
        sample_range = np.arange(np.ceil(np.max(calc_sample_range)))
        calc_range_m = sample_range / sample_rate * sound_speed / 2
        tvg_curves = spreading * np.ma.log10(calc_range_m) + 2 * (alpha / 1000) * calc_range_m

        # Create the output data dictionary
        data_out = {
            'backscatter_data': bs_corrected,
            'tvg_curves': tvg_curves,
            'tvg_beam_values': tvg_matrix
        }
        return data_out

    @classmethod
    def remove_tvg_simple_curve(cls,
                                spreading: float,
                                alpha: float,
                                sample_rate: np.ndarray,
                                bottom_detection_point: np.ma.MaskedArray,
                                sound_speed: np.ndarray,
                                backscatter: np.ma.MaskedArray):

        sample_rate = sample_rate[:, np.newaxis]
        sound_speed = sound_speed[:, np.newaxis]

        range_m = bottom_detection_point / sample_rate * sound_speed / 2
        tvg_matrix = spreading * np.ma.log10(range_m) + 2 * (alpha / 1000) * range_m

        bs_corrected = backscatter - np.ma.masked_invalid(tvg_matrix)

        # Create an example tvg curve to store
        calc_max_range = np.ma.max(np.ma.max(range_m)) + 5
        calc_sample_range = calc_max_range * sample_rate * 2 / sound_speed
        sample_range = np.arange(np.ceil(np.max(calc_sample_range)))
        calc_range_m = sample_range / sample_rate * sound_speed / 2
        tvg_curves = spreading * np.ma.log10(calc_range_m) + 2 * (alpha / 1000) * calc_range_m

        # Create the output data dictionary
        data_out = {
            'backscatter_data': bs_corrected,
            'tvg_curves': tvg_curves,
            'tvg_beam_values': tvg_matrix
        }
        return data_out
