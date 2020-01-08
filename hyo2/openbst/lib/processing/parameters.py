import logging

from hyo2.openbst.lib.processing.raw_decoding import RawDecodeParameters
from hyo2.openbst.lib.processing.static_gain_compensation import StaticGainParameters

logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.rawdecode = RawDecodeParameters()
        self.static_gains = StaticGainParameters()
