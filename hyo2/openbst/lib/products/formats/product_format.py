from abc import ABC, abstractmethod
import logging

import gdal
from netCDF4 import Dataset

from hyo2.openbst.lib.products.product_meta import ProductMeta

logger = logging.getLogger(__name__)


class ProductFormat(ABC):

    def __init__(self, path: str, nc: Dataset):
        self.path = path
        self.nc = nc
        self.meta = ProductMeta()

    def retrieve_spatial_info_with_gdal(self):
        # logger.debug("retrieving spatial info with GDAL")

        try:

            ds = gdal.OpenEx(self.path)
            if ds is None:
                logger.warning("unable to open the file")
                return False

            self.meta.crs = ds.GetProjection()
            if self.meta.crs is None:
                logger.warning("unable to get CRS")
                return False
            # logger.debug("crs: %s" % self.meta.crs)

            self.meta.gt = ds.GetGeoTransform()
            if self.meta.gt is None:
                logger.warning("unable to get geotransform")
                return False
            # logger.debug("gt: %s" % (self.meta.gt,))

            self.meta.x_res = self.meta.gt[1]
            self.meta.y_res = self.meta.gt[5]
            # logger.debug("res -> x: %s, y: %s" % (self._x_res, self._y_res))
            self.meta.x_min = self.meta.gt[0] + self.meta.x_res * 0.5
            self.meta.x_max = self.meta.gt[0] + (self.meta.x_res * (ds.RasterXSize - 1)) + self.meta.x_res * 0.5

            self.meta.y_min = self.meta.gt[3] + (self.meta.y_res * (ds.RasterYSize - 1)) + self.meta.y_res * 0.5
            self.meta.y_max = self.meta.gt[3] + self.meta.y_res * 0.5

            # logger.debug("x -> min: %s, max: %s" % (self.meta.x_min, self.meta.x_max))
            # logger.debug("y -> min: %s, max: %s" % (self.meta.y_min, self.meta.y_max))

            # TODO: check for possible issues
            self.meta.y_res = abs(self.meta.y_res)  # make y always positive

            self.meta.has_spatial_info = True
            # noinspection PyUnusedLocal
            ds = None

            return True

        except Exception as e:
            logger.warning("while using GDAL, %s" % e)
            return False

    @abstractmethod
    def convert(self) -> int:
        return 0

    # noinspection PyUnusedLocal
    @abstractmethod
    def export(self) -> int:
        return 0
