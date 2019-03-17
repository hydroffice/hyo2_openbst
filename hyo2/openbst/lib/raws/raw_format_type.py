from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RawFormatType(Enum):

    UNKNOWN = 0
    KNG_ALL = 1
    KNG_KMALL = 2
