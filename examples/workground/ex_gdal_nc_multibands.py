import logging
import os

from hyo2.abc.lib.testing import Testing
# from hyo2.openbst.app import app_info  # for gdal

from osgeo import gdal
from osgeo import osr
import numpy as np

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

# fake source
np.random.seed(0)
ny = 120
nx = 160
arr1 = np.random.rand(nx, ny)
arr2 = np.random.rand(nx, ny)
arr3 = np.random.rand(nx, ny)
gt = (360988.700, 0.200, 0.000, 4769988.900, 0.000, -0.200)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

nc_path = os.path.normpath(os.path.join(testing.output_data_folder(), "gdal.nc"))
logger.debug("gdal nc path: %s" % nc_path)

dst_drv = gdal.GetDriverByName('netCDF')
dst_ds = dst_drv.Create(nc_path, ny, nx, 1, gdal.GDT_Float32)
dst_ds.SetGeoTransform(gt)    # specify coords
srs = osr.SpatialReference()            # establish encoding
srs.ImportFromEPSG(32619)                # WGS84 lat/long
dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
# write bathymetry
dst_ds.GetRasterBand(1).SetDescription("Bathymetry")
dst_ds.GetRasterBand(1).SetNoDataValue(np.nan)
dst_ds.GetRasterBand(1).WriteArray(arr1)
# # write uncertainty
# dst_ds.GetRasterBand(2).SetDescription("Uncertainty")
# dst_ds.GetRasterBand(2).SetNoDataValue(np.nan)
# dst_ds.GetRasterBand(2).WriteArray(arr2)
# # write density
# dst_ds.GetRasterBand(3).SetDescription("Density")
# dst_ds.GetRasterBand(3).SetNoDataValue(np.nan)
# dst_ds.GetRasterBand(3).WriteArray(arr3)
dst_ds.FlushCache()                     # write to disk
dst_ds = None                           # save, close
# logger.debug("driver: %s" % dst_drv)
