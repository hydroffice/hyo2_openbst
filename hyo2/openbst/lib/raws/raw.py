import logging
import os
from bidict import bidict

logger = logging.getLogger(__name__)

from hyo2.openbst.lib.raws.raw_format_type import RawFormatType
from hyo2.openbst.lib.raws.raw_layer_type import RawLayerType


class Raw:

    data_type_prefix = bidict({
        RawLayerType.UNKNOWN: "UNK",
        RawLayerType.NAVIGATION: "NAV",
        RawLayerType.PITCH: "PIT",
        RawLayerType.ROLL: "ROL",
        RawLayerType.HEAVE: "HEV",
    })

    @classmethod
    def make_layer_key(cls, path: str, data_type: RawLayerType) -> str:
        path_basename = os.path.basename(path)
        raw_prefix = Raw.data_type_prefix[data_type]
        return "%s:%s" % (path_basename, raw_prefix)

    @classmethod
    def retrieve_layer_and_format_types(cls, path: str) -> dict:

        raw_types = dict()

        path_ext = os.path.splitext(path)[-1].lower()

        if path_ext in [".all", ".wcd"]:
            raw_types[RawLayerType.NAVIGATION] = RawFormatType.KNG_ALL
            raw_types[RawLayerType.PITCH] = RawFormatType.KNG_ALL
            raw_types[RawLayerType.ROLL] = RawFormatType.KNG_ALL
            raw_types[RawLayerType.HEAVE] = RawFormatType.KNG_ALL

        elif path_ext in [".kmall", ".kmwcd"]:
            raw_types[RawLayerType.NAVIGATION] = RawFormatType.KNG_KMALL
            raw_types[RawLayerType.PITCH] = RawFormatType.KNG_KMALL
            raw_types[RawLayerType.ROLL] = RawFormatType.KNG_KMALL
            raw_types[RawLayerType.HEAVE] = RawFormatType.KNG_KMALL

        return raw_types
