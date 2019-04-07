import logging

import gdal
import numpy as np
from netCDF4 import Dataset

from hyo2.openbst.lib.products.formats.product_format import ProductFormat
from hyo2.openbst.lib.products.formats.product_format_type import ProductFormatType
from hyo2.openbst.lib.products.product_layer import ProductLayer
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType

logger = logging.getLogger(__name__)


class ProductFormatGeoTiff(ProductFormat):

    def __init__(self, path: str, nc: Dataset) -> None:
        super().__init__(path=path, nc=nc)
        self._ds = None

    def convert(self) -> int:

        # success = self.retrieve_spatial_info_with_gdal()
        # if not success:
        #     logger.error("issue in retrieving spatial info with GDAL: %s" % self.path)
        #
        # data_layers = dict()
        #
        # try:
        #     self._ds = gdal.OpenEx(self.path, gdal.GA_Update)  # we need to be able to update the file
        # except Exception as e:
        #     logger.error("while opening, %s" % e)
        #     return data_layers
        #
        # if self._ds is None:
        #     logger.error("Error in reading the GDAL dataset")
        #     return data_layers
        #
        # for layer_type in layer_types:
        #
        #     if layer_type != ProductLayerType.MOSAIC:
        #         logger.warning("unsupported layer type: %s" % layer_type)
        #         continue
        #
        #     layer = ProductLayer(layer_type=layer_type, format_type=ProductFormatType.GEOTIFF)
        #
        #     try:
        #         layer.array = self._ds.ReadAsArray()
        #     except Exception as e:
        #         logger.error("while reading GDAL band as array', %s" % e)
        #         return data_layers
        #
        #     try:
        #         nodata = self._ds.GetRasterBand(1).GetNoDataValue()
        #     except Exception as e:
        #         logger.error("while reading nodata value for GDAL band', %s" % e)
        #         return data_layers
        #
        #     layer.array[layer.array == nodata] = np.nan
        #     layer.array = np.flipud(layer.array)
        #     logger.debug("data array: %s" % (layer.array.shape, ))
        #
        #     layer.meta = self.meta
        #
        #     data_layers[layer_type] = layer

        self.nc.sync()
        return 0

    def export(self) -> int:

        # try:
        #     self._ds = gdal.Open(self.path, gdal.GA_Update)  # we need to be able to update the file
        # except Exception as e:
        #     logger.error("while opening, %s" % e)
        #     return False
        #
        # if self._ds is None:
        #     logger.error("Error in reading the GDAL dataset")
        #     return False
        #
        # for layer_type in data_layers.keys():
        #
        #     if layer_type != ProductLayerType.MOSAIC:
        #         logger.warning("unsupported layer type: %s" % layer_type)
        #         continue
        #
        #     layer = data_layers[layer_type]
        #
        #     array = layer.array[:]
        #
        #     array[np.isnan(array)] = -9999.0
        #     array = np.flipud(array)
        #     self._ds.GetRasterBand(1).WriteArray(array)
        #     self._ds = None
        #
        # try:
        #     self._ds = gdal.Open(self.path, gdal.GA_Update)  # we need to be able to update the file
        #     self._ds = None
        #
        # except Exception as e:
        #     logger.error("while re-opening, %s" % e)
        #     return False

        return 0
