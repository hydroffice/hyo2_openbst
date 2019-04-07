from bidict import bidict
from enum import Enum


class ProductLayerType(Enum):
    UNKNOWN = 0
    BATHYMETRY = 1
    UNCERTAINTY = 2
    DESIGNATED = 3
    MOSAIC = 4


layer_type_prefix = bidict({
    ProductLayerType.UNKNOWN: "UNK",
    ProductLayerType.BATHYMETRY: "BAT",
    ProductLayerType.UNCERTAINTY: "UNC",
    ProductLayerType.DESIGNATED: "DES",
    ProductLayerType.MOSAIC: "MOS"
})
