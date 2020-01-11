import logging

from hyo2.openbst.lib.processing.process_methods.dicts import ProcessMethods
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeParameters
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainParameters

logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.rawdecode = RawDecodeParameters()
        self.static_gains = StaticGainParameters()

    # TODO: Can there be a check here to create object if not yet created
    def get_process_params(self, process_type: ProcessMethods):
        if process_type == ProcessMethods.RAWDECODE:
            return self.rawdecode
        elif process_type == ProcessMethods.STATICGAIN:
            return self.static_gains