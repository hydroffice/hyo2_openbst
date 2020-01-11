import logging

from hyo2.openbst.lib.processing.process_types.dicts import ProcessTypes
from hyo2.openbst.lib.processing.process_types.raw_decoding import RawDecodeParameters
from hyo2.openbst.lib.processing.process_types.static_gain_compensation import StaticGainParameters

logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.rawdecode = RawDecodeParameters()
        self.static_gains = StaticGainParameters()

    # TODO: Can there be a check here to create object if not yet created
    def get_process_params(self, process_type: ProcessTypes):
        if process_type == ProcessTypes.RAWDECODE:
            return self.rawdecode
        elif process_type == ProcessTypes.STATICGAIN:
            return self.static_gains