import logging
import os
from hyo2.abc.lib.testing import Testing
from hyo2.abc.lib.logging import set_logging
from hyo2.openbst.app import app_info  # for gdal
from osgeo import gdal
from osgeo import osr
import numpy as np

set_logging(ns_list=["hyo2.openbst"])
logger = logging.getLogger(__name__)

# settings
ny = 1200
nx = 1600
res = 1000.0
nr_bands = 3  # 3
epsg = 32619  # WGS 84 / UTM zone 19N

# fake source
np.random.seed(0)
arr1 = np.random.rand(nx, ny)
arr2 = np.random.rand(nx, ny)
arr3 = np.random.rand(nx, ny)
gt = (360988.700, res, 0.000, 4769988.900, 0.000, -res)

# output path
testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
if nr_bands == 1:
    nc_path = os.path.normpath(os.path.join(testing.output_data_folder(), "gdal_1band.nc"))
elif nr_bands == 3:
    nc_path = os.path.normpath(os.path.join(testing.output_data_folder(), "gdal_3bands.nc"))
else:
    raise RuntimeError("invalid number of bands: %d" % nr_bands)
logger.debug("gdal nc path: %s" % nc_path)

# write file header
dst_drv = gdal.GetDriverByName('netCDF')
dst_ds = dst_drv.Create(nc_path, ny, nx, nr_bands, gdal.GDT_Float32)
dst_ds.SetGeoTransform(gt)  # specify coords
srs = osr.SpatialReference()
srs.ImportFromEPSG(epsg)
dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file

# write file data
if nr_bands in [1, 3]:
    # write bathymetry
    dst_ds.GetRasterBand(1).SetDescription("Bathymetry")
    dst_ds.GetRasterBand(1).SetNoDataValue(np.nan)
    dst_ds.GetRasterBand(1).WriteArray(arr1)
if nr_bands in [3, ]:
    # write uncertainty
    dst_ds.GetRasterBand(2).SetDescription("Uncertainty")
    dst_ds.GetRasterBand(2).SetNoDataValue(np.nan)
    dst_ds.GetRasterBand(2).WriteArray(arr2)
    # write density
    dst_ds.GetRasterBand(3).SetDescription("Density")
    dst_ds.GetRasterBand(3).SetNoDataValue(np.nan)
    dst_ds.GetRasterBand(3).WriteArray(arr3)

# finalize data writing
dst_ds.FlushCache()  # write to disk
dst_ds = None  # save, close
# logger.debug("driver: %s" % dst_drv)
