import logging
import numpy as np

from enum import Enum
from netCDF4 import Dataset, Group
from typing import Union

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.auxilaries.ssp import SSPEnum
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceParams

logger = logging.getLogger(__name__)


# ## Transmission Loss Compensation Enum and Dictionaries ##
class TransmissionLossEnum(Enum):
    spherical = 0
    cylindrical = 1
    hybrid = 2
    guiseppe = 3


transmission_loss_title = {
    TransmissionLossEnum.spherical: "Corrected Backscatter - Transmission Loss Corrected: Spherical",
    TransmissionLossEnum.cylindrical: "Corrected Backscatter - Transmission Loss Corrected: Cylindrical",
    TransmissionLossEnum.hybrid: "Corrected Backscatter - Transmission Loss Corrected: Hybrid",
    TransmissionLossEnum.guiseppe: "Corrected Backscatter - Transmission Loss Corrected: Guiseppe Method"
}


# ## Transmission Loss Parameter Object ##
class TransmissonLossParameters:
    process_name = "transmission_loss_correction"

    def __init__(self):
        self.method_type = TransmissionLossEnum.spherical
        self.use_ssp = False
        self.ssp_nearest_in = SSPEnum.nearest_in_time

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = transmission_loss_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.use_ssp = str(self.use_ssp)
            grp_process.ssp_nearest_in = self.ssp_nearest_in.name
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = TransmissonLossParameters.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
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
                        parent: str, parameters: TransmissonLossParameters) -> Union[dict, bool]:
        p_method_type = parameters.method_type
        p_use_ssp = parameters.use_ssp
        p_ssp_nearest_in = parameters.ssp_nearest_in

        # TODO: There is an issue here. If I do not do the right order, i wont be able to find the right data. I may
        #  have solved this but there is no time to vet fully

        data_backscatter = cls.find_bs_data(ds_process=ds_process, parent=parent)
        data_raypath = cls.find_ray_data(ds_process=ds_process, parent=parent)

        if data_backscatter is None:
            logger.error("Step not computed: Backscatter data not found")
            return False

        if data_raypath is None:
            logger.error("Step not computed: Raypath data not found")
            return False

        if p_method_type is TransmissionLossEnum.spherical:
            # FIXME: This alpha value is really a static gain and should be treated as such. I need to figure out a way
            #   to more appropriately grab absorption values or make an assumption on what it is.
            grp_runtime = ds_raw.groups['runtime_settings']
            var_absorption = grp_runtime.variables['absorption_gain']
            data_absorption = var_absorption[:]
            data_absorption = data_absorption[:, np.newaxis]

            data_out = cls.spherical_correction(backscatter=data_backscatter,
                                                ray_path=data_raypath,
                                                alpha=data_absorption)

        elif p_method_type is TransmissionLossEnum.cylindrical:
            pass
        elif p_method_type is TransmissionLossEnum.hybrid:
            pass
        elif p_method_type is TransmissionLossEnum.guiseppe:
            pass
        else:
            raise TypeError("Unrecognized Method Type: %s" % p_method_type)
        return data_out

    @classmethod
    def write_data_to_nc(cls,data_dict: dict, grp_process: Group):
        try:
            grp_process.createDimension(dimname='ping', size=None)
            grp_process.createDimension(dimname='beam', size=None)

            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))

                    var_bs_data[:] = data

                elif data_name == 'trasmission_loss':
                    var_tl_data = grp_process.createVariable(varname='transmission_loss_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_tl_data[:] = data
                elif data_name == 'spreading_loss':
                    var_sp_data = grp_process.createVariable(varname='spreading_loss_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_sp_data[:] = data

                elif data_name == 'absorption_loss':
                    var_ab_data = grp_process.createVariable(varname='absorption_loss_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_ab_data[:] = data
            return True
        except RuntimeError:
            return False

    # # Processing Methods Types #
    @classmethod
    def spherical_correction(cls,
                             backscatter: np.ma.MaskedArray,
                             ray_path: np.ma.MaskedArray,
                             alpha: Union[float, np.ma.MaskedArray] = 0.0):

        spreading_loss = 20 * np.ma.log10(ray_path)
        absorption_loss = alpha / 1000 * ray_path
        transmission_loss = 2 * spreading_loss + 2 * absorption_loss

        bs_corrected = backscatter + transmission_loss

        # Output dictionary of data
        data_out = {
            'backscatter_data': bs_corrected,
            'transmission_loss': transmission_loss,
            'spreading_loss': spreading_loss,
            'absorption_loss': absorption_loss
        }
        return data_out

    @classmethod
    def cylindrical_correction(cls):
        pass

    @classmethod
    def hybrid_correction(cls):
        pass

    @classmethod
    def guiseppe_correction(cls):
        pass

    # Helper Functions
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
