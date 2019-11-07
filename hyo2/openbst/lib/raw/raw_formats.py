from enum import Enum
from pathlib import Path


class RawFormatType(Enum):

    UNKNOWN = 0
    KNG_ALL = 1
    KNG_KMALL = 2
    KNG_WCD = 3
    RESON_S7K = 4
    RESON_7K = 5
    R2SONIC_S7K = 6

    @classmethod
    def retrieve_format_types(cls, path: Path):
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


raw_format_dict = {
    RawFormatType.UNKNOWN: "Unknown Format",
    RawFormatType.KNG_ALL: "Kongsberg .all",
    RawFormatType.KNG_KMALL: "Kongsberg .kmall",
    RawFormatType.KNG_WCD: "Kongsberg .wcd",
    RawFormatType.RESON_7K: "Reson .7k",
    RawFormatType.RESON_S7K: "Reson .s7k",
    RawFormatType.R2SONIC_S7K: "R2Sonic .s7k"
}   # TODO: Check the r2sonic extension
