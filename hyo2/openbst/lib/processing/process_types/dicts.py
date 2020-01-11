import logging

from enum import Enum

logger = logging.getLogger(__name__)


class ProcessTypes(Enum):
    RAWDECODE = 0
    INTERPOLATION = 1
    STATICGAIN = 2
    TVG = 3
    MANUFACTURERGAIN = 4
    SOURCELEVEL = 5
    CALIBRATION = 6
    GEOLOCATION = 7
    GRIDDING = 8
    TRANSMISSIONLOSS = 9
    INSONIFIEDAREA = 10
    ANGULARDEPENDENCE = 11
    DESPECKLE = 12
    ANTIALIASING = 13


process_requirements = {
    ProcessTypes.RAWDECODE: None,
    ProcessTypes.INTERPOLATION: None,
    ProcessTypes.STATICGAIN: ProcessTypes.RAWDECODE,
    ProcessTypes.TVG: ProcessTypes.RAWDECODE,
    ProcessTypes.MANUFACTURERGAIN: ProcessTypes.RAWDECODE,
    ProcessTypes.SOURCELEVEL: ProcessTypes.RAWDECODE,
    ProcessTypes.CALIBRATION: ProcessTypes.RAWDECODE,
    ProcessTypes.GEOLOCATION: ProcessTypes.INTERPOLATION,
    ProcessTypes.GRIDDING: ProcessTypes.GEOLOCATION,
    ProcessTypes.TRANSMISSIONLOSS: ProcessTypes.RAWDECODE,
    ProcessTypes.INSONIFIEDAREA: ProcessTypes.INTERPOLATION,
    ProcessTypes.ANGULARDEPENDENCE: ProcessTypes.INSONIFIEDAREA,
    ProcessTypes.DESPECKLE: None,
    ProcessTypes.ANTIALIASING: None
}