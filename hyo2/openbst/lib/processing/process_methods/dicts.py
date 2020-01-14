import logging

from enum import Enum

logger = logging.getLogger(__name__)


class ProcessMethods(Enum):
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
    ProcessMethods.RAWDECODE: None,
    ProcessMethods.INTERPOLATION: None,
    ProcessMethods.STATICGAIN: ProcessMethods.RAWDECODE,
    ProcessMethods.TVG: ProcessMethods.RAWDECODE,
    ProcessMethods.MANUFACTURERGAIN: ProcessMethods.RAWDECODE,
    ProcessMethods.SOURCELEVEL: ProcessMethods.RAWDECODE,
    ProcessMethods.CALIBRATION: ProcessMethods.RAWDECODE,
    ProcessMethods.GEOLOCATION: ProcessMethods.INTERPOLATION,
    ProcessMethods.GRIDDING: ProcessMethods.GEOLOCATION,
    ProcessMethods.TRANSMISSIONLOSS: ProcessMethods.RAWDECODE,
    ProcessMethods.INSONIFIEDAREA: ProcessMethods.INTERPOLATION,
    ProcessMethods.ANGULARDEPENDENCE: ProcessMethods.INSONIFIEDAREA,
    ProcessMethods.DESPECKLE: None,
    ProcessMethods.ANTIALIASING: None
}