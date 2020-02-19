import logging

from hyo2.openbst.lib.processing.process_methods.dicts import ProcessMethods

from hyo2.openbst.lib.processing.process_methods.area_correction import AreaCorrectionParameters
from hyo2.openbst.lib.processing.process_methods.calibration import CalibrationParameters
from hyo2.openbst.lib.processing.process_methods.interpolation import InterpParameters
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeParameters
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceParams
from hyo2.openbst.lib.processing.process_methods.source_level import SourceLevelParameters
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainParameters
from hyo2.openbst.lib.processing.process_methods.transmission_loss import TransmissonLossParameters
from hyo2.openbst.lib.processing.process_methods.tvg import TVGCorrectionParameters


logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.area_correction = AreaCorrectionParameters()
        self.calibration = CalibrationParameters()
        self.rawdecode = RawDecodeParameters()
        self.static_gains = StaticGainParameters()
        self.source_level = SourceLevelParameters()
        self.tvg = TVGCorrectionParameters()
        self.interpolation = InterpParameters()
        self.raytrace = RayTraceParams()
        self.transmissionloss = TransmissonLossParameters()

    # TODO: Can there be a check here to create object if not yet created
    def get_process_params(self, process_type: ProcessMethods):
        if process_type == ProcessMethods.RAWDECODE:
            return self.rawdecode
        elif process_type == ProcessMethods.INSONIFIEDAREA:
            return self.area_correction
        elif process_type == ProcessMethods.CALIBRATION:
            return self.calibration
        elif process_type == ProcessMethods.INTERPOLATION:
            return self.interpolation
        elif process_type == ProcessMethods.STATICGAIN:
            return self.static_gains
        elif process_type == ProcessMethods.SOURCELEVEL:
            return self.source_level
        elif process_type == ProcessMethods.TVG:
            return self.tvg
        elif process_type == ProcessMethods.RAYTRACE:
            return self.raytrace
        elif process_type == ProcessMethods.TRANSMISSIONLOSS:
            return self.transmissionloss
