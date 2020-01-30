import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Transmission Loss Compensation Enum and Dictionaries ##
class TransmissionLossEnum(Enum):
    spherical = 0
    cylindrical = 1
    hybrid = 2
    guiseppe = 3

class SSPEnum(Enum):
    nearest_in_time = 0
    nearest_in_location = 1


transmission_loss_title = {
    TransmissionLossEnum.spherical: "Corrected Backscatter - Transmission Loss Corrected: Spherical",
    TransmissionLossEnum.cylindrical: "Corrected Backscatter - Transmission Loss Corrected: Cylindrical",
    TransmissionLossEnum.hybrid: "Corrected Backscatter - Transmission Loss Corrected: Hybrid"
    TransmissionLossEnum.guiseppe: "Corrected Backscatter - Transmission Loss Corrected: Guiseppe Method"
}


# ## Transmission Loss Parameter Object ##
class TransmissonLossParameters:
    process_name = "transmission_loss_correction"

    def __init__(self):
        self.method_type = TransmissionLossEnum.spherical
        self.use_ssp = False
        self.ssp_nearest_in = SSPEnum.nearest_in_time

    def nc_write_parameters(self, grp_process:Group):
        try:
            grp_process.title = transmission_loss_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.use_ssp = str(self.use_ssp)
            grp_process.ssp_nearest_in = self.ssp_nearest_in.name
            return True
        except TypeError:
            return False

    def process_identifiers(self) ->  list:
        process_string = TransmissonLossParameters.process_name
        parameter_string = str()
        for key ,value in self.__dict__.items():
            parameter_string += key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


# ## Transmission Loss class and methods ##
class TransmissonLoss:

    def __init__(self):
        pass

    @classmethod
    def tl_compensation(cls, ds_process: Dataset, ds_raw: Dataset,
                        parent: str, parameters: TransmissonLossParameters) -> dict:
        p_method_type = parameters.method_type
        p_use_ssp = parameters.use_ssp
        p_ssp_nearest_in = parameters.ssp_nearest_in
        pass

    @classmethod
    def write_data_to_nc(cls,data_dict: dict, grp_process: Group):
        pass

    # # Processing Methods Types #
    @classmethod
    def spherical_correction(cls):
        pass

    @classmethod
    def cylindrical_correction(cls):
        pass

    @classmethod
    def hybrid_correction(cls):
        pass

    @classmethod
    def guiseppe_correction(cls):
        pass
    