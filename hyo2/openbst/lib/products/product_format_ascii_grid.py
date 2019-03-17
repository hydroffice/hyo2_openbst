import logging
import os

import gdal
import numpy as np

from hyo2.openbst.lib.products.product_format import ProductFormat
from hyo2.openbst.lib.products.product_format_type import ProductFormatType
from hyo2.openbst.lib.products.product_layer import ProductLayer

logger = logging.getLogger(__name__)


class ProductFormatASCIIGrid(ProductFormat):

    def __init__(self, path: str) -> None:
        super().__init__(path=path)

    def read_data_types(self, layer_types: list) -> dict:

        if len(layer_types) != 1:
            raise RuntimeError("Too many layers for ASCII Grid format")

        success = self.retrieve_spatial_info_with_gdal()
        if not success:
            logger.error("issue in retrieving spatial info with GDAL: %s" % self.path)

        data_layers = dict()

        try:
            ds = gdal.Open(self.path, gdal.GA_Update)  # we need to be able to update the file
        except Exception as e:
            logger.error("while opening, %s" % e)
            return data_layers

        if ds is None:
            logger.error("Error in reading the GDAL dataset")
            return data_layers

        for layer_type in layer_types:

            layer = ProductLayer(layer_type=layer_type, format_type=ProductFormatType.ASC_GRID)

            try:
                layer.array = ds.ReadAsArray()
            except Exception as e:
                logger.error("while reading GDAL band as array', %s" % e)
                return data_layers

            try:
                nodata = ds.GetRasterBand(1).GetNoDataValue()
            except Exception as e:
                logger.error("while reading nodata value for GDAL band', %s" % e)
                return data_layers

            layer.array[layer.array == nodata] = np.nan
            layer.array = np.flipud(layer.array)
            logger.debug("elevation array: %s" % (layer.array.shape, ))

            layer.meta = self.meta

            data_layers[layer_type] = layer

        return data_layers

    def save_data_types(self, data_layers: dict) -> bool:

        if len(data_layers) != 1:
            raise RuntimeError("Too many layers for ASCII Grid format")

        no_data = -9999.0

        tmp_path = self.path + ".tmp"
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        os.rename(self.path, tmp_path)

        # open the tmp dataset
        try:
            input_ds = gdal.OpenEx(tmp_path, gdal.GA_Update)  # we need to be able to update the file
        except Exception as e:
            logger.error("while opening, %s" % e)
            return False

        # create an in-memory dataset and populate with input dataset info
        driver = gdal.GetDriverByName('MEM')
        mem_ds = driver.Create("", input_ds.RasterXSize, input_ds.RasterYSize,
                               input_ds.RasterCount, gdal.GDT_Float32)
        mem_ds.SetProjection(input_ds.GetProjection())
        mem_ds.SetGeoTransform(input_ds.GetGeoTransform())

        try:
            # noinspection PyUnusedLocal
            input_ds = None
        except Exception as e:
            logger.error("while creating in memory data set, %s" % e)
            return False

        for layer_type in data_layers.keys():

            layer = data_layers[layer_type]

            arr = layer.array[:]

            arr[np.isnan(arr)] = no_data
            arr = np.flipud(arr)
            mem_ds.GetRasterBand(1).WriteArray(arr)
            mem_ds.GetRasterBand(1).SetNoDataValue(no_data)

        try:
            driver = gdal.GetDriverByName('AAIGrid')
            output_ds = driver.CreateCopy(self.path, mem_ds, options=['DECIMAL_PRECISION=3', ])
        except Exception as e:
            logger.error("while creating, %s" % e)
            return False

        if output_ds is None:
            logger.error("Error in creating the GDAL dataset")
            return False

        try:
            _ = gdal.Open(self.path, gdal.GA_Update)  # we need to be able to update the file
            _ = None
        except Exception as e:
            logger.error("while re-opening, %s" % e)
            return False

        return True
