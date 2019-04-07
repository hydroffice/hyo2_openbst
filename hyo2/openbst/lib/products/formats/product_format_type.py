from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProductFormatType(Enum):

    UNKNOWN = 0
    BAG = 1
    GEOTIFF = 2
    ASC_GRID = 3
