import logging

from hyo2.openbst.lib.processing.process_types.raw_decoding import RawDecodeParameters
from hyo2.openbst.lib.processing.process_types.static_gain_compensation import StaticGainParameters

logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.rawdecode = RawDecodeParameters()
        self.static_gains = StaticGainParameters()
