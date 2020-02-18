import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Optional

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Calibration Enum and Dictionaries ##
class RadiationPatternEnum(Enum):
    calibration_file = 0
    custom_curve = 1


radiation_pattern_title = {
    RadiationPatternEnum.calibration_file: "Corrected Backscatter - Compensated Radiation Pattern using Calibration "
                                           "File",
    RadiationPatternEnum.custom_curve: "Corrected Backscatter - Compensated Radiation Pattern using a Fitted Curve"
}


# ## Radiation Pattern Parameters Object ##
class RadiationPatternParameters:
    process_name = "radiation_pattern_compensation"

    def __init__(self):
        self.method_type = RadiationPatternEnum.calibration_file
        self.fit_curve = True
        self.curve_order = 2

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = radiation_pattern_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.fit_curve = str(self.fit_curve)
            grp_process.curve_order = self.curve_order
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = RadiationPatternParameters.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


# Radiation Pattern Class and Methods ##
class RadiationPatternCorrection:

    def __init__(self):
        pass

    @classmethod
    def radiation_pattern_correction(cls, ds_process: Dataset, ds_raw: Dataset, ds_aux: Dataset,
                                     parent: str, parameters: RadiationPatternParameters,
                                     calibration_list: Optional[list] = None):
        p_method_type = parameters.method_type

        if p_method_type is RadiationPatternEnum.calibration_file:
            # Check if there is a calibration file
            if len(calibration_list) < 1:
                logger.warning("No calibration file found in: %s" % ds_aux.path)
                return False

            p_fit_curve = parameters.fit_curve
            p_curve_order = parameters.curve_order

            # extract required variables
            # TODO:This is a hack I need to find a way to intelligently select a calibration file
            #   will need to do checking for frequency
            grp_cal = ds_aux.groups['calibration_files'].goups[calibration_list[0]]
            var_angles = grp_cal.variables['angles']
            data_angles = var_angles[:]
            data_angles = data_angles[:, np.newaxis]
            var_cal = grp_cal.variables['calibration_value']
            data_cal = var_cal[:]
            data_cal = data_cal[:, np.newaxis]

            grp_parent = ds_process.groups[parent]
            var_backscatter = grp_parent.groups['backscatter_data']
            data_backscatter = var_backscatter[:]

            grp_raw = ds_raw.groups['raw_bathymetry_data']
            var_rx_angle = grp_raw.variables['rx_angle']
            data_rx_angle = var_rx_angle[:]

            # function call
            data_out = cls.calibration_file(backscatter_data=data_backscatter, bs_angles=data_rx_angle,
                                            cal_curve_angles=data_angles, cal_curve_values=data_cal,
                                            fit_curve=p_fit_curve, curve_order=p_curve_order)

        elif p_method_type is RadiationPatternEnum.custom_curve:
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
            grp_process.createDimension(dimname='angle',size=None)

            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_bs_data[:] = data
                elif data_name == 'calibration_values':
                    var_cal_val = grp_process.createVariable(varname='calibration_correction_values',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_cal_val[:] = data

                elif data_name == 'calibration_curve_angles':
                    var_curve_angles = grp_process.createVariable(varname='angle',
                                                                  datatype='f8',
                                                                  dimensions=('angle',))
                    var_curve_angles[:] = data

                elif data_name == "calibration_curve_values":
                    var_curve_val = grp_process.createVariable(varname='calibration_curve',
                                                               datatype='f8',
                                                               dimensions=('angle',))
                    var_curve_val[:] = data
            return True

        except RuntimeError:
            return False

    @classmethod
    def calibration_file(cls, backscatter_data: np.ma.MaskedArray,
                         bs_angles: np.ma.MaskedArray,
                         cal_curve_angles: np.ma.MaskedArray,
                         cal_curve_values: np.ma.MaskedArray,
                         fit_curve: bool,
                         curve_order: int):

        num_ping = backscatter_data.shape[0]
        # If fit curve is true, fit a curve
        if fit_curve is True:
            poly_coefficents = np.polyfit(cal_curve_angles, cal_curve_values, curve_order)
            cal_curve_angles = np.arange(-75, 75, 0.1)[:, np.newaxis]
            cal_curve_values = np.polyval(poly_coefficents, cal_curve_angles)

        # loop through pings and fit to curve
        calibration_values = np.ones(shape=backscatter_data.shape) * np.nan
        for ping in num_ping:
            calibration_values[ping, :] = np.interp(bs_angles, cal_curve_angles, cal_curve_values)

        # correct bs values
        bs_corrected = backscatter_data - calibration_values

        # write to dictionary
        data_out = {
            'backscatter_data': bs_corrected,
            'calibration_values': calibration_values,
            'calibration_curve_angles': cal_curve_angles,
            'calibration_curve_values': cal_curve_values
        }

        return data_out

    @classmethod
    def custom_curve(cls):
        pass
    