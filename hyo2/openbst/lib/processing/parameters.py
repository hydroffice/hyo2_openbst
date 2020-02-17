import logging

from hyo2.openbst.lib.processing.process_methods.dicts import ProcessMethods

from hyo2.openbst.lib.processing.process_methods.interpolation import InterpParameters
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeParameters
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainParameters
from hyo2.openbst.lib.processing.process_methods.source_level import SourceLevelParameters
from hyo2.openbst.lib.processing.process_methods.tvg import TVGCorrectionParameters
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceParams

logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.rawdecode = RawDecodeParameters()
        self.static_gains = StaticGainParameters()
        self.source_level = SourceLevelParameters()
        self.tvg = TVGCorrectionParameters()
        self.interpolation = InterpParameters()
        self.raytrace = RayTraceParams()

    # TODO: Can there be a check here to create object if not yet created
    def get_process_params(self, process_type: ProcessMethods):
        if process_type == ProcessMethods.RAWDECODE:
            return self.rawdecode
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
