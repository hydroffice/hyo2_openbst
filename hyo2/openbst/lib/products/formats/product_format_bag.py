import logging

import numpy as np
from h5py import File
from lxml import etree
from netCDF4 import Dataset

from hyo2.openbst.lib.products.formats.product_format import ProductFormat
from hyo2.openbst.lib.products.formats.product_format_type import ProductFormatType
from hyo2.openbst.lib.products.product_layer import ProductLayer
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType

logger = logging.getLogger(__name__)


class ProductFormatBag(ProductFormat):

    ns = {
        'bag': 'http://www.opennavsurf.org/schema/bag',
        'gco': 'http://www.isotc211.org/2005/gco',
        'gmd': 'http://www.isotc211.org/2005/gmd',
        'gmi': 'http://www.isotc211.org/2005/gmi',
        'gml': 'http://www.opengis.net/gml/3.2',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    ns2 = {
        'gml': 'http://www.opengis.net/gml',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'smXML': 'http://metadata.dgiwg.org/smXML',
    }

    # noinspection PyBroadException
    @classmethod
    def is_vr(cls, path) -> bool:

        try:
            file = File(path, 'r')
            bag_root = file['BAG_root']
            _ = bag_root['varres_refinements']
            return True

        except Exception:
            return False

    def __init__(self, path: str, nc: Dataset) -> None:
        super().__init__(path=path, nc=nc)

        self._file = None
        self._bag_root = None
        self._elevation = None
        self._uncertainty = None
        self._tracking_list = None
        self._meta_xml = None

        self._xml_tree = None
        self._xml_rows = None
        self._xml_cols = None

    def convert(self) -> int:

        success = self.retrieve_spatial_info_with_gdal()  # to avoid to interfere with the h5py stuff
        if not success:
            logger.warning("issue in retrieving spatial info with GDAL -> directly reading the XML Metadata")

        data_layers = list()

        try:
            self._file = File(self.path, 'r')  # we need read an existing file

        except Exception as e:
            logger.error("while opening, %s" % e)
            return 0

        try:
            self._bag_root = self._file['BAG_root']
        except Exception as e:
            logger.error("while reading 'BAG_root', %s" % e)
            return 0

        if not self.meta.has_spatial_info:
            self._retrieve_spatial_info()

        try:
            self._elevation = self._bag_root['elevation']
        except Exception as e:
            logger.error("while reading 'BAG_root/elevation', %s" % e)
            return 0

        # create y dimension variable
        self.nc.createDimension('y', self._elevation.shape[0])
        y_var = self.nc.createVariable('y', 'f8', ('y',))
        y_var.standard_name = 'projection_y_coordinate'
        y_var.long_name = 'y coordinate of projection'
        y_var.units = 'm'
        y_var._CoordinateAxisType = "GeoY"
        y_var[:] = [self.meta.y_min + r * self.meta.y_res for r in range(self._elevation.shape[0])]

        # create x dimension variable
        self.nc.createDimension('x', self._elevation.shape[1])
        x_var = self.nc.createVariable('x', 'f8', ('x',))
        x_var.standard_name = 'projection_x_coordinate'
        x_var.long_name = 'x coordinate of projection'
        x_var.units = 'm'
        x_var._CoordinateAxisType = "GeoX"
        x_var[:] = [self.meta.x_min + c * self.meta.x_res for c in range(self._elevation.shape[1])]

        # create crs variable
        var = self.nc.createVariable('crs', 'S1')
        var.GeoTransform = " ".join("%.3f" % c for c in self.meta.gt)
        # logger.debug("GeoTransform: %s" % ncd.root.GeoTransform)
        crs = str(self.meta.crs)
        logger.debug("%s" % crs)
        var.spatial_ref = crs
        var._CoordinateTransformType = "Projection"
        var._CoordinateAxisTypes = "GeoX GeoY"

        # create bathymetry
        var = self.nc.createVariable('bathymetry', 'f4', ('y', 'x'),
                                     zlib=False, least_significant_digit=3, fill_value=np.nan)
        var.long_name = "Bathymetry"
        var.grid_mapping = "crs"
        array = self._elevation[()]
        array[array == 1000000.0] = np.nan
        var[:, :] = array

        # try:
        #     self._uncertainty = self._bag_root['uncertainty']
        #     var = self.nc.createVariable('uncertainty', 'f4', ('y', 'x'),
        #                                  zlib=False, least_significant_digit=3, fill_value=np.nan)
        #     var.long_name = "Uncertainty"
        #     var.grid_mapping = "crs"
        #     array = self._uncertainty[()]
        #     array[array == 1000000.0] = np.nan
        #     var[:, :] = array
        # except Exception as e:
        #     logger.error("while reading 'BAG_root/uncertainty', %s" % e)

        #     elif layer_type == ProductLayerType.DESIGNATED:
        #
        #         try:
        #             self._tracking_list = self._bag_root['tracking_list']
        #         except Exception as e:
        #             logger.error("while reading 'BAG_root/tracking_list', %s" % e)
        #             continue
        #
        #         logger.debug("tracking list: %d" % (len(self._tracking_list), ))
        #         for idx, item in enumerate(self._tracking_list):
        #
        #             feature = dict()
        #             for name in item.dtype.names:
        #                 feature[name] = item[name]
        #             feature['x'], feature['y'] = layer.cr2xy(feature['col'], feature['row'])
        #             feature['flagged'] = False
        #
        #             # logger.info("%d feature -> %s" % (idx, feature))
        #             layer.features[idx] = feature
        #
        #     else:
        #
        #         logging.info("Skipping unsupported layer type: %s" % layer_type)
        #         continue
        #
        #     if layer.is_raster():
        #         if not self._check_shape_validity(layer.array.shape):
        #             continue
        #
        #     data_layers[layer_type] = layer

        self.nc.sync()
        return 0

    def _retrieve_spatial_info(self) -> bool:

        self._meta_xml = self._bag_root['metadata'][:].tostring()
        # logger.debug("xml: %s[...]" % self._meta_xml[:20])

        self._xml_tree = etree.fromstring(self._meta_xml)

        self._read_wkt_prj()
        # logger.debug("crs -> %s" % (self._crs, ))

        # rows and cols
        self._xml_rows = None
        self._xml_cols = None
        self._read_rows_and_cols()

        # resolution along x and y axes
        self._read_res_x_and_y()
        # logger.warning("res -> x: %s, y: %s" % (self.meta.x_res, self.meta.y_res))

        # corner SW and NE
        self._read_corners_sw_and_ne()
        # logger.debug("x -> min: %s, max: %s" % (self.meta.x_min, self.meta.x_max))
        # logger.debug("y -> min: %s, max: %s" % (self.meta.y_min, self.meta.y_max))

        self.meta.has_spatial_info = True

        return True

    def _read_wkt_prj(self):
        """ attempts to read the WKT projection string """

        try:
            ret = self._xml_tree.xpath('//*/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/'
                                       'gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString',
                                       namespaces=self.ns)
        except etree.Error as e:
            logger.warning("unable to read the WKT projection string: %s" % e)
            return

        if len(ret) == 0:
            try:
                ret = self._xml_tree.xpath('//*/referenceSystemInfo/smXML:MD_CRS',
                                           namespaces=self.ns2)
            except etree.Error as e:
                logger.warning("unable to read the WKT projection string: %s" % e)
                return

            if len(ret) != 0:
                logger.warning("unsupported method to describe CRS")
                return

        try:
            self.meta.crs = ret[0].text

        except (ValueError, IndexError) as e:
            logger.warning("unable to read the WKT projection string: %s" % e)
            return

    def _read_rows_and_cols(self):
        """ attempts to read rows and cols info """

        try:
            ret = self._xml_tree.xpath('//*/gmd:spatialRepresentationInfo/gmd:MD_Georectified/'
                                       'gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:dimensionSize/gco:Integer',
                                       namespaces=self.ns)
        except etree.Error as e:
            logger.warning("unable to read rows and cols: %s" % e)
            return

        if len(ret) == 0:

            try:
                ret = self._xml_tree.xpath('//*/spatialRepresentationInfo/smXML:MD_Georectified/'
                                           'axisDimensionProperties/smXML:MD_Dimension/dimensionSize',
                                           namespaces=self.ns2)
            except etree.Error as e:
                logger.warning("unable to read rows and cols: %s" % e)
                return

        try:
            self._xml_rows = int(ret[0].text)
            self._xml_cols = int(ret[1].text)

        except (ValueError, IndexError) as e:
            logger.warning("unable to read rows and cols: %s" % e)
            return

    def _read_res_x_and_y(self):
        """ attempts to read resolution along x- and y- axes """

        try:
            ret = self._xml_tree.xpath('//*/gmd:spatialRepresentationInfo/gmd:MD_Georectified/'
                                       'gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:resolution/gco:Measure',
                                       namespaces=self.ns)
        except etree.Error as e:
            logger.warning("unable to read res x and y: %s" % e)
            return

        if len(ret) == 0:

            try:
                ret = self._xml_tree.xpath('//*/spatialRepresentationInfo/smXML:MD_Georectified/'
                                           'axisDimensionProperties/smXML:MD_Dimension/resolution/'
                                           'smXML:Measure/smXML:value',
                                           namespaces=self.ns2)
            except etree.Error as e:
                logger.warning("unable to read res x and y: %s" % e)
                return

        try:
            self.meta.x_res = float(ret[0].text)
            self.meta.y_res = float(ret[1].text)

        except (ValueError, IndexError) as e:
            logger.warning("unable to read res x and y: %s" % e)
            return

    def _read_corners_sw_and_ne(self):
        """ attempts to read corners SW and NE """

        try:
            ret = self._xml_tree.xpath('//*/gmd:spatialRepresentationInfo/gmd:MD_Georectified/'
                                       'gmd:cornerPoints/gml:Point/gml:coordinates',
                                       namespaces=self.ns)[0].text.split()
        except (etree.Error, IndexError):
            try:
                ret = self._xml_tree.xpath('//*/spatialRepresentationInfo/smXML:MD_Georectified/'
                                           'cornerPoints/gml:Point/gml:coordinates',
                                           namespaces=self.ns2)[0].text.split()
            except (etree.Error, IndexError) as e:
                logger.warning("unable to read corners SW and NE: %s" % e)
                return

        try:
            sw = [float(c) for c in ret[0].split(',')]
            ne = [float(c) for c in ret[1].split(',')]

        except (ValueError, IndexError) as e:
            logger.warning("unable to read corners SW and NE: %s" % e)
            return

        # logger.debug("sw: %s" % sw)
        self.meta.x_min = sw[0] + self.meta.x_res * 0.5
        self.meta.x_max = ne[0] - self.meta.x_res * 0.5
        self.meta.y_min = sw[1] + self.meta.y_res * 0.5
        self.meta.y_max = ne[1] - self.meta.y_res * 0.5

    # def _check_shape_validity(self, array_shape: tuple) -> bool:
    #
    #     if (self._xml_rows is None) or (self._xml_cols is None):
    #         return True
    #
    #     if (self._xml_rows != array_shape[0]) or (self._xml_cols != array_shape[1]):
    #         logger.warning("shape -> xml (%s, %s) != (%s, %s)"
    #                        % (self._xml_rows, self._xml_cols, array_shape[0], array_shape[1]))
    #         return False
    #
    #     return True

    def export(self) -> int:

        # try:
        #     self._file = File(self.path, 'r+')  # we need read and write an existing file
        #
        # except Exception as e:
        #     logger.error("while opening, %s" % e)
        #     return False
        #
        # try:
        #     self._bag_root = self._file['BAG_root']
        # except Exception as e:
        #     logger.error("while reading 'BAG_root', %s" % e)
        #     return False
        #
        # for layer_type in data_layers.keys():
        #
        #     layer = data_layers[layer_type]
        #
        #     if layer_type == ProductLayerType.BATHYMETRY:
        #
        #         try:
        #             self._elevation = self._bag_root['elevation']
        #         except Exception as e:
        #             logger.error("while reading 'BAG_root/elevation', %s" % e)
        #             continue
        #
        #         array = layer.array[:]
        #
        #         min_new = np.nanmin(array)
        #         max_new = np.nanmax(array)
        #
        #         array[np.isnan(array)] = 1000000.0
        #         self._elevation[...] = array
        #
        #         try:
        #             min_old = self._elevation.attrs['Minimum Elevation Value']
        #             max_old = self._elevation.attrs['Maximum Elevation Value']
        #             logger.debug("old min/max elevation: %f/%f" % (min_old, max_old))
        #         except Exception as e:
        #             logger.warning("issue with reading Elevation attributes: %s" % e)
        #
        #         # noinspection PyStringFormat
        #         logger.debug("new min/max elevation: %f/%f" % (min_new, max_new))
        #
        #         self._elevation.attrs['Minimum Elevation Value'] = min_new
        #         self._elevation.attrs['Maximum Elevation Value'] = max_new
        #
        #         layer.modified = False
        #         continue
        #
        #     elif layer_type == ProductLayerType.UNCERTAINTY:
        #
        #         try:
        #             self._uncertainty = self._bag_root['uncertainty']
        #         except Exception as e:
        #             logger.error("while reading 'BAG_root/uncertainty', %s" % e)
        #             continue
        #
        #         array = layer.array[:]
        #
        #         min_new = np.nanmin(array)
        #         max_new = np.nanmax(array)
        #
        #         array[np.isnan(array)] = 1000000.0
        #         self._uncertainty[...] = array
        #
        #         try:
        #             min_old = self._uncertainty.attrs['Minimum Uncertainty Value']
        #             max_old = self._uncertainty.attrs['Maximum Uncertainty Value']
        #             logger.debug("old min/max uncertainty: %f/%f" % (min_old, max_old))
        #         except Exception as e:
        #             logger.warning("issue with reading Uncertainty attributes: %s" % e)
        #
        #         # noinspection PyStringFormat
        #         logger.debug("new min/max uncertainty: %f/%f" % (min_new, max_new))
        #
        #         self._uncertainty.attrs['Minimum Uncertainty Value'] = min_new
        #         self._uncertainty.attrs['Maximum Uncertainty Value'] = max_new
        #
        #         layer.modified = False
        #         continue
        #
        #     elif layer_type == ProductLayerType.DESIGNATED:
        #
        #         try:
        #             self._tracking_list = self._bag_root['tracking_list'][()]
        #         except Exception as e:
        #             logger.error("while reading 'BAG_root/tracking_list', %s" % e)
        #             continue
        #
        #         for feature in layer.features.values():
        #
        #             if not feature['flagged']:
        #                 continue
        #
        #             for idx, item in enumerate(self._tracking_list):
        #                 if (feature['row'] == item['row']) and (feature['col'] == item['col']):
        #                     self._tracking_list = np.delete(self._tracking_list, idx)
        #
        #         del self._bag_root['tracking_list']
        #         self._bag_root['tracking_list'] = self._tracking_list
        #
        #         layer.modified = False
        #         continue
        #
        #     else:
        #
        #         logging.info("Skipping unsupported layer type: %s" % layer_type)
        #         continue
        #
        # self._file.flush()

        return 0
