from enum import Enum


class LayerType(Enum):
    UNKNOWN = 0
    BATHYMETRY = 1
    UNCERTAINTY = 2
    DESIGNATED = 3
    MOSAIC = 4
