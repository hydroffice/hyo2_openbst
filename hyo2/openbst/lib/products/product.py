import logging
import os

from bidict import bidict

from hyo2.openbst.lib.products.product_format import ProductFormatType
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType
from hyo2.openbst.lib.products.product_format_bag import ProductFormatBag
from hyo2.openbst.lib.products.product_format_geotiff import ProductFormatGeoTiff
from hyo2.openbst.lib.products.product_format_ascii_grid import ProductFormatASCIIGrid

logger = logging.getLogger(__name__)


class Product:

    data_type_prefix = bidict({
        ProductLayerType.UNKNOWN: "UNK",
        ProductLayerType.BATHYMETRY: "BAT",
        ProductLayerType.UNCERTAINTY: "UNC",
        ProductLayerType.DESIGNATED: "DES",
        ProductLayerType.MOSAIC: "MOS"
    })

    @classmethod
    def make_layer_key(cls, path: str, data_type: ProductLayerType) -> str:
        path_basename = os.path.basename(path)
        raster_prefix = Product.data_type_prefix[data_type]
        return "%s:%s" % (raster_prefix, path_basename)

    @classmethod
    def retrieve_layer_and_format_types(cls, path: str,
                                        hint_type: ProductLayerType = ProductLayerType.UNKNOWN) -> dict:

        raster_types = dict()

        path_ext = os.path.splitext(path)[-1].lower()

        if path_ext in [".asc", ]:

            if hint_type == ProductLayerType.UNKNOWN:  # default to Bathymetry
                raster_types[ProductLayerType.BATHYMETRY] = ProductFormatType.ASC_GRID
            else:
                raster_types[hint_type] = ProductFormatType.ASC_GRID

        elif path_ext in [".bag", ]:
            # we currently only read the two mandatory layers for SR BAG
            raster_types[ProductLayerType.BATHYMETRY] = ProductFormatType.BAG
            raster_types[ProductLayerType.UNCERTAINTY] = ProductFormatType.BAG
            raster_types[ProductLayerType.DESIGNATED] = ProductFormatType.BAG

        elif path_ext in [".tif", ".tiff"]:
            raster_types[ProductLayerType.MOSAIC] = ProductFormatType.GEOTIFF

        else:
            raster_types[ProductLayerType.UNKNOWN] = ProductFormatType.UNKNOWN

        return raster_types

    @classmethod
    def load(cls, input_path: str, input_format: ProductFormatType, layer_types: list) -> dict:

        if input_format == ProductFormatType.BAG:
            fmt = ProductFormatBag(path=input_path)

        elif input_format == ProductFormatType.GEOTIFF:
            fmt = ProductFormatGeoTiff(path=input_path)

        elif input_format == ProductFormatType.ASC_GRID:
            fmt = ProductFormatASCIIGrid(path=input_path)

        else:
            logger.warning("unknown/unsupported format type: %s" % input_format)
            return dict()

        layers = fmt.read_data_types(layer_types=layer_types)
        if len(layers) == 0:
            logging.warning("issue in reading the data types from input source")
            return dict()

        return layers

    @classmethod
    def save(cls, output_path: str, output_format: ProductFormatType, output_layers: dict) -> bool:

        logger.debug("save %d layers in %s as %s"
                     % (len(output_layers), output_path, output_format))

        if output_format == ProductFormatType.BAG:
            fmt = ProductFormatBag(path=output_path)

        elif output_format == ProductFormatType.GEOTIFF:
            fmt = ProductFormatGeoTiff(path=output_path)

        elif output_format == ProductFormatType.ASC_GRID:
            fmt = ProductFormatASCIIGrid(path=output_path)

        else:
            logger.warning("unknown/unsupported format type: %s" % output_format)
            return False

        return fmt.save_data_types(data_layers=output_layers)
