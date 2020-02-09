import logging
# import numpy as np

from enum import Enum
from netCDF4 import Dataset

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
        self.fit_curve = False
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
    def radiation_pattern_correction(cls):
        pass

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        pass

    @classmethod
    def calibration_file(cls):
        pass

    @classmethod
    def custom_curve(cls):
        pass
    