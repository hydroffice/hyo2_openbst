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
    RAYTRACE = 7
    GEOLOCATION = 8
    GRIDDING = 9
    TRANSMISSIONLOSS = 10
    INSONIFIEDAREA = 11
    ANGULARDEPENDENCE = 12
    DESPECKLE = 13
    ANTIALIASING = 14


process_requirements = {
    ProcessMethods.RAWDECODE: None,
    ProcessMethods.INTERPOLATION: None,
    ProcessMethods.STATICGAIN: ProcessMethods.RAWDECODE,
    ProcessMethods.TVG: ProcessMethods.RAWDECODE,
    ProcessMethods.MANUFACTURERGAIN: ProcessMethods.RAWDECODE,
    ProcessMethods.SOURCELEVEL: ProcessMethods.RAWDECODE,
    ProcessMethods.CALIBRATION: ProcessMethods.RAWDECODE,
    ProcessMethods.RAYTRACE: ProcessMethods.INTERPOLATION,
    ProcessMethods.GEOLOCATION: ProcessMethods.RAYTRACE,
    ProcessMethods.GRIDDING: ProcessMethods.GEOLOCATION,
    ProcessMethods.TRANSMISSIONLOSS: ProcessMethods.RAYTRACE,
    ProcessMethods.INSONIFIEDAREA: ProcessMethods.INTERPOLATION,
    ProcessMethods.ANGULARDEPENDENCE: ProcessMethods.INSONIFIEDAREA,
    ProcessMethods.DESPECKLE: None,
    ProcessMethods.ANTIALIASING: None
}