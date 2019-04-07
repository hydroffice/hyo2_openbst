import logging
from osgeo import gdal
from osgeo import osr
import numpy as np

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

# fake data source
np.random.seed(0)
ny = 120
nx = 160
arr1 = np.random.rand(nx, ny)
gt = (360988.700, 0.200, 0.000, 4769988.900, 0.000, -0.200)
# output file
nc_path = "gdal.nc"

# prepare netCDF file
dst_drv = gdal.GetDriverByName('netCDF')
dst_ds = dst_drv.Create(nc_path, ny, nx, 1, gdal.GDT_Float32)
dst_ds.SetGeoTransform(gt)
srs = osr.SpatialReference()
srs.ImportFromEPSG(32619)
dst_ds.SetProjection(srs.ExportToWkt())

# write band
dst_ds.GetRasterBand(1).SetDescription("Bathymetry")
dst_ds.GetRasterBand(1).SetNoDataValue(np.nan)
dst_ds.GetRasterBand(1).WriteArray(arr1)

# finalize to disk and close
dst_ds.FlushCache()
dst_ds = None
