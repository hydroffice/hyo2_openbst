import logging
import os
from osgeo import osr
from osgeo import osr
from pyproj import Geod
import numpy as np

logger = logging.getLogger(__name__)


def forward(lon_in, lat_in, azimuth, distance, units='m'):
    geo = Geod(ellps='WGS84')
    lon_out, lat_out, _ = geo.fwd(lons=lon_in, lats=lat_in, az=azimuth, dist=distance, radians=False)

    return lon_out, lat_out


def beam_alignment(data, numbeams):
    beam_number = set(data[0, :])
    beam_range = set(range(numbeams))

