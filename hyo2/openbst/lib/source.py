import logging
import os

from bidict import bidict

from hyo2.openbst.lib.sources.format import FormatType
from hyo2.openbst.lib.sources.layer import LayerType
from hyo2.openbst.lib.sources.bag import Bag
from hyo2.openbst.lib.sources.geotiff import GeoTiff
from hyo2.openbst.lib.sources.ascii_grid import ASCIIGrid

logger = logging.getLogger(__name__)


class Source:

    data_type_prefix = bidict({
        LayerType.UNKNOWN: "UNK",
        LayerType.BATHYMETRY: "BAT",
        LayerType.UNCERTAINTY: "UNC",
        LayerType.DESIGNATED: "DES",
        LayerType.MOSAIC: "MOS"
    })

    @classmethod
    def make_layer_key(cls, path: str, data_type: LayerType) -> str:
        path_basename = os.path.basename(path)
        raster_prefix = Source.data_type_prefix[data_type]
        return "%s:%s" % (raster_prefix, path_basename)

    @classmethod
    def retrieve_layer_and_format_types(cls, path: str,
                                        hint_type: LayerType = LayerType.UNKNOWN) -> dict:

        raster_types = dict()

        path_ext = os.path.splitext(path)[-1].lower()

        if path_ext in [".asc", ]:

            if hint_type == LayerType.UNKNOWN:  # default to Bathymetry
                raster_types[LayerType.BATHYMETRY] = FormatType.ASC_GRID
            else:
                raster_types[hint_type] = FormatType.ASC_GRID

        elif path_ext in [".bag", ]:
            # we currently only read the two mandatory layers for SR BAG
            raster_types[LayerType.BATHYMETRY] = FormatType.BAG
            raster_types[LayerType.UNCERTAINTY] = FormatType.BAG
            raster_types[LayerType.DESIGNATED] = FormatType.BAG

        elif path_ext in [".tif", ".tiff"]:
            raster_types[LayerType.MOSAIC] = FormatType.GEOTIFF

        else:
            raster_types[LayerType.UNKNOWN] = FormatType.UNKNOWN

        return raster_types

    @classmethod
    def load(cls, input_path: str, input_format: FormatType, layer_types: list) -> dict:

        if input_format == FormatType.BAG:
            fmt = Bag(path=input_path)

        elif input_format == FormatType.GEOTIFF:
            fmt = GeoTiff(path=input_path)

        elif input_format == FormatType.ASC_GRID:
            fmt = ASCIIGrid(path=input_path)

        else:
            logger.warning("unknown/unsupported format type: %s" % input_format)
            return dict()

        layers = fmt.read_data_types(layer_types=layer_types)
        if len(layers) == 0:
            logging.warning("issue in reading the data types from input source")
            return dict()

        return layers

    @classmethod
    def save(cls, output_path: str, output_format: FormatType, output_layers: dict) -> bool:

        logger.debug("save %d layers in %s as %s"
                     % (len(output_layers), output_path, output_format))

        if output_format == FormatType.BAG:
            fmt = Bag(path=output_path)

        elif output_format == FormatType.GEOTIFF:
            fmt = GeoTiff(path=output_path)

        elif output_format == FormatType.ASC_GRID:
            fmt = ASCIIGrid(path=output_path)

        else:
            logger.warning("unknown/unsupported format type: %s" % output_format)
            return False

        return fmt.save_data_types(data_layers=output_layers)
