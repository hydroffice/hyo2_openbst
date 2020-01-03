import logging

from hyo2.openbst.lib.processing.raw_decoding import RawDecodeParameters

logger = logging.getLogger(__name__)


class Parameters:
    """Class to store processing parameters"""

    def __init__(self):
        self.rawdecode = RawDecodeParameters()
