import logging
from enum import Enum
from pathlib import Path

from hyo2.openbst.lib.raw.reson import Reson
logger = logging.getLogger(__name__)


class RawFormatType(Enum):

    UNKNOWN = 0
    KNG_ALL = 1
    KNG_KMALL = 2
    KNG_WCD = 3
    RESON_S7K = 4
    RESON_7K = 5
    R2SONIC_S7K = 6


class Raw:

    def __init__(self, raw_path: Path):
        self._path = raw_path

        self.file_object = None
        self.rawformat = self.retrieve_format_types(raw_path)

        if self.rawformat == RawFormatType.UNKNOWN:
            self.valid = False
            return
        else:
            self.valid = True

        self.file_object = self.create_raw(self.rawformat)

    @property
    def path(self):
        return self._path

    def create_raw(self, raw_format: RawFormatType):
        raw = None
        if raw_format is RawFormatType.KNG_ALL:
            pass                                            # TODO: Create the Kongsberg parser
        elif raw_format is RawFormatType.KNG_KMALL:
            pass
        elif raw_format is RawFormatType.KNG_WCD:
            pass
        elif raw_format is RawFormatType.RESON_S7K:
            raw = Reson(self.file_path)
            if raw.file_valid is True:
                raw.data_map()
        elif raw_format is RawFormatType.RESON_7K:
            raw = Reson(self.file_path)
            if raw.file_valid is True:
                raw.data_map()
        elif raw_format is RawFormatType.R2SONIC_S7K:
            pass                                            # TODO: Create R2Sonic Parser

        return raw

    def validate(self):
        pass

    @classmethod
    def retrieve_format_types(cls, path: Path) -> RawFormatType:
        fileparts = path.name.split('.')
        extention = fileparts[-1]

        if extention == 'all':
            raw_format = RawFormatType.KNG_ALL
        elif extention == 'kmall':
            raw_format = RawFormatType.KNG_KMALL
        elif extention == 'wcd':
            raw_format = RawFormatType.KNG_WCD
        elif extention == 's7k':
            raw_format = RawFormatType.RESON_S7K
        elif extention == '7k':
            raw_format = RawFormatType.RESON_7K
        elif extention == 'r2sc':
            raw_format = RawFormatType.R2SONIC_S7K
        else:
            raw_format = RawFormatType.UNKNOWN

        return raw_format
