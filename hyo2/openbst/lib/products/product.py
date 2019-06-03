import logging
import os
from pathlib import Path
from datetime import datetime
from netCDF4 import Dataset, date2num, num2date
import numpy as np

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.lib import lib_info

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.products.formats.product_format_type import ProductFormatType
from hyo2.openbst.lib.products.formats.product_format_bag import ProductFormatBag
from hyo2.openbst.lib.products.formats.product_format_geotiff import ProductFormatGeoTiff
from hyo2.openbst.lib.products.formats.product_format_ascii_grid import ProductFormatASCIIGrid

logger = logging.getLogger(__name__)


class Product:

    product_ext = ".nc"

    @classmethod
    def make_product_path(cls, project_folder: Path, product_name: str):
        return project_folder.joinpath("products", product_name + cls.product_ext).resolve()

    def __init__(self, project_folder: Path, source_path: Path):
        self._project_folder = project_folder
        self._source_path = source_path

        self._name = self._source_path.name
        self._hash = NetCDFHelper.hash_string(str(self._source_path))
        self._path = self.make_product_path(project_folder=self._project_folder,
                                            product_name=self._hash)

        self._product = None
        self._nc()

    @property
    def project_folder(self) -> Path:
        return self._project_folder

    @property
    def source_path(self) -> Path:
        return self._source_path

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def conventions(self) -> str:
        return self._ds.Conventions

    @property
    def time_units(self) -> str:
        return self._ds.variables["time"].units

    @property
    def time_calendar(self) -> str:
        return self._ds.variables["time"].calendar

    @property
    def version(self) -> str:
        return self._ds.version

    @property
    def created(self) -> datetime:
        return num2date(self._ds.created, units=self.time_units, calendar=self.time_calendar)

    @property
    def modified(self):
        return num2date(self._ds.modified, units=self.time_units, calendar=self.time_calendar)

    def _nc(self) -> None:
        if self._path.exists():
            open_mode = "a"
        else:
            open_mode = "w"

        self._ds = Dataset(filename=str(self._path), mode=open_mode)

        NetCDFHelper.init(ds=self._ds)
        logger.debug("conventions: %s" % self.conventions)
        logger.debug("time: %s [%s]" % (self.time_units, self.time_calendar))
        logger.debug("version: %s" % self.version)
        logger.debug("created: %s" % self.created)
        logger.debug("modified: %s" % self.modified)

        # if open_mode == "w":
        #     self._make_netcdf()
        #
        # else:
        #     self._time = self._product.variables["time"]
        #     self._check_source_changed()
        #
        #     if self.product_version > lib_info.lib_version:
        #         raise RuntimeError("Product has a future version: %s" % self.product_version)
        #     self._time = self._product.variables["time"]
        #     if not os.path.exists(self.source_path) and not self.product_unlinked:
        #         self._product.unlinked = 1
        #         self._product.sync()
        #         logger.warning("Product unlinked: %s" % self.source_path)
        #
        # logger.debug("open in '%s' mode: [%s] %s"
        #              % (open_mode, self.product_version, self.product_path))

    def updated(self):
        NetCDFHelper.update_modified(self._ds)

    # def _make_netcdf(self):
    #     self._product.Conventions = 'CF-1.6'
    #     self._product.standard_name_vocabulary = 'CF Standard Name Table (v26, 08 November 2013)'
    #
    #     # Create time coordinate
    #     tdim = self._product.createDimension('time', None)
    #     self._time = self._product.createVariable('time', np.float64, (tdim.name,))
    #     self._time.units = 'milliseconds since 1970-01-01T00:00:00'
    #     self._time.calendar = 'gregorian'
    #
    #     self._product.product_version = lib_info.lib_version
    #     self._product.product_creation = date2num(datetime.utcnow(), self._time.units, self._time.calendar)
    #     self._product.source_path = self._source_path
    #     file_sz, mod_timestamp = Helper.file_size_timestamp(self.source_path)
    #     mod_timestamp = mod_timestamp.replace(tzinfo=None)
    #     self._product.source_size = file_sz
    #     self._product.source_date = date2num(mod_timestamp, self._time.units, self._time.calendar)
    #     self._product.unlinked = 0
    #     self._product.sync()
    #
    #     self._convert_from_source()
    #
    # def _check_source_changed(self):
    #     file_sz, mod_timestamp = Helper.file_size_timestamp(self.source_path)
    #     mod_timestamp = mod_timestamp.replace(tzinfo=None)
    #     overwrite_required = (self.source_date != mod_timestamp) or (file_sz != self.source_size)
    #     logger.info("Overwrite required: %s" % overwrite_required)
    #
    #     if overwrite_required:
    #         # close and remove
    #         self.close()
    #         os.remove(self.product_path)
    #
    #         # create and rebuild
    #         self._product = Dataset(filename=self._product_path, mode="w")
    #         self._make_netcdf()
    #
    # def _convert_from_source(self) -> bool:
    #     input_format = self.retrieve_format_type(self.source_path)
    #     if input_format == ProductFormatType.BAG:
    #         fmt = ProductFormatBag(path=self.source_path, nc=self._product)
    #
    #     elif input_format == ProductFormatType.GEOTIFF:
    #         fmt = ProductFormatGeoTiff(path=self.source_path, nc=self._product)
    #
    #     elif input_format == ProductFormatType.ASC_GRID:
    #         fmt = ProductFormatASCIIGrid(path=self.source_path, nc=self._product)
    #
    #     else:
    #         logger.warning("unknown/unsupported format type: %s" % input_format)
    #         return False
    #
    #     nr_of_layers = fmt.convert()
    #     if nr_of_layers == 0:
    #         logging.warning("issue in reading the data from input source")
    #         return False
    #
    #     return True

    # def close(self) -> None:
    #     if self._product:
    #         self._product.close()
    #         self._product = None
    #
    # @property
    # def product_name(self) -> str:
    #     return self._product_name
    #
    # @property
    # def product_path(self) -> Path:
    #     return self._product_path
    #
    # @property
    # def product_version(self) -> str:
    #     return self._product.product_version
    #
    # @property
    # def product_creation(self) -> datetime:
    #     return num2date(self._product.setup_creation, units=self._time.units, calendar=self._time.calendar)
    #
    # @property
    # def product_unlinked(self) -> str:
    #     return self._product.unlinked
    #
    # @property
    # def source_path(self) -> str:
    #     return self._product.source_path
    #
    # @property
    # def source_size(self) -> int:
    #     return self._product.source_size
    #
    # @property
    # def source_date(self) -> str:
    #     return num2date(self._product.source_date, units=self._time.units, calendar=self._time.calendar)

    # @classmethod
    # def make_layer_key(cls, path: str, data_type: ProductLayerType) -> str:
    #     path_basename = os.path.basename(path)
    #     raster_prefix = Product.data_type_prefix[data_type]
    #     return "%s:%s" % (raster_prefix, path_basename)

    # @classmethod
    # def retrieve_format_type(cls, path: str) -> ProductFormatType:
    #     path_ext = os.path.splitext(path)[-1].lower()
    #
    #     if path_ext in [".asc", ]:
    #         return ProductFormatType.ASC_GRID
    #
    #     if path_ext in [".bag", ]:
    #         return ProductFormatType.BAG
    #
    #     if path_ext in [".tif", ".tiff"]:
    #         return ProductFormatType.GEOTIFF
    #
    #     return ProductFormatType.UNKNOWN

    # @classmethod
    # def save(cls, output_path: str, output_format: ProductFormatType, output_layers: dict) -> bool:
    #
    #     logger.debug("save %d layers in %s as %s"
    #                  % (len(output_layers), output_path, output_format))
    #
    #     if output_format == ProductFormatType.BAG:
    #         fmt = ProductFormatBag(path=output_path)
    #
    #     elif output_format == ProductFormatType.GEOTIFF:
    #         fmt = ProductFormatGeoTiff(path=output_path)
    #
    #     elif output_format == ProductFormatType.ASC_GRID:
    #         fmt = ProductFormatASCIIGrid(path=output_path)
    #
    #     else:
    #         logger.warning("unknown/unsupported format type: %s" % output_format)
    #         return False
    #
    #     return fmt.save_data_types(data_layers=output_layers)

    # ### OTHER ###

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <name: %s>\n" % self.name
        msg += "  <path: %s>\n" % self.path
        msg += "  <conventions: %s>\n" % self.conventions
        msg += "  <time: %s [%s]>\n" % (self.time_units, self.time_calendar)
        msg += "  <version: %s>\n" % self.version
        msg += "  <created: %s>\n" % self.created
        msg += "  <modified: %s>\n" % self.modified
        return msg
