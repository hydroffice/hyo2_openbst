import logging

from datetime import datetime
from pathlib import Path
from netCDF4 import Dataset, Group, num2date

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.raw.raw_formats import RawFormatType

logger = logging.getLogger(__name__)


class ProjectInfo:

    def __init__(self, prj_path: Path) -> None:
        self._path = prj_path.joinpath("info.nc")
        self._ds = None
        self._raws_name = "raws"
        self._products_name = "products"
        self._nc()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def project_path(self) -> Path:
        return self._path.parent

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

    @property
    def raws_group(self) -> Group:
        return self._ds.groups[self._raws_name]

    @property
    def raws(self):
        return self.raws_group.variables

    @property
    def project_raws(self) -> list:
        project_raws = list()
        for raw_key, raw in self.raws.items():
            if raw.deleted == 0:
                project_raws.append(raw_key)
        return project_raws

    @property
    def products_group(self) -> Group:
        return self._ds.groups[self._products_name]

    @property
    def products(self):
        return self.products_group.variables

    @property
    def valid_products(self) -> list:
        valid_products = list()
        for product_key, product in self.products.items():
            if product.deleted == 0:
                valid_products.append(product_key)
        return valid_products

    def _nc(self) -> None:
        if self._path.exists():
            open_mode = "a"
        else:
            open_mode = "w"
        self._ds = Dataset(filename=self._path, mode=open_mode)

        NetCDFHelper.init(ds=self._ds)

        # logger.debug("conventions: %s" % self.conventions)
        # logger.debug("time: %s [%s]" % (self.time_units, self.time_calendar))
        # logger.debug("version: %s" % self.version)
        # logger.debug("created: %s" % self.created)
        # logger.debug("modified: %s" % self.modified)

        NetCDFHelper.groups(ds=self._ds, names=[self._raws_name, self._products_name])

        logger.info("open in '%s' mode: [v.%s] %s" % (open_mode, self.version, self.path))

    def updated(self):
        NetCDFHelper.update_modified(self._ds)

    # # ### RAWS ###

    def add_raw(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("does not exist: %s" % path)
            return False

        raw_fmt = RawFormatType.retrieve_format_type(path=path)
        if raw_fmt is RawFormatType.UNKNOWN:
            logger.warning("unrecognized raw input type: %s" % path)
            return False

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.raws.keys():
            try:                                            # TODO: Why are we trying ...
                if self.raws[path_hash].deleted == 1:
                    self.raws[path_hash].deleted = 0
                    self.raws[path_hash].valid = 0
                    logger.info("previously deleted: %s" % path)
                else:
                    logger.info("file already in project: %s" % path)
            except AttributeError:
                self.raws[path_hash].valid = 0
                self.raws[path_hash].deleted = 0

        else:
            path_var = self.raws_group.createVariable(path_hash, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            path_var.linked = 1
            path_var.imported = 0
            logger.info("added: %s" % path)

        self.updated()
        return True

    def remove_raw(self, path: Path) -> bool:

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raws.keys():
            logger.info("absent: %s" % path)
            return False

        self.raws[path_hash].deleted = 1
        logger.info("removed: %s" % path)

        self._ds.sync()
        return True

    # # ### PRODUCTS ###

    def add_product(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("does not exist: %s" % path)
            return False

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.products.keys():
            try:
                if self.products[path_hash].deleted == 1:
                    self.products[path_hash].deleted = 0
                    logger.info("previously deleted: %s" % path)
            except AttributeError:
                self.products[path_hash].deleted = 0
        else:
            path_var = self.products_group.createVariable(path_hash, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            logger.debug("added: %s" % path)

        self._ds.sync()
        return True

    def remove_product(self, path: Path) -> bool:

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.products.keys():
            logger.info("absent: %s" % path)
            return False

        self.products[path_hash].deleted = 1
        logger.debug("removed: %s" % path)

        self._ds.sync()
        return True

    # ### OTHER ###

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <name: %s>\n" % self.name
        msg += "  <project path: %s>\n" % self.project_path
        msg += "  <conventions: %s>\n" % self.conventions
        msg += "  <time: %s [%s]>\n" % (self.time_units, self.time_calendar)
        msg += "  <version: %s>\n" % self.version
        msg += "  <created: %s>\n" % self.created
        msg += "  <modified: %s>\n" % self.modified
        msg += "  <raws: %d [%d]>\n" % (len(self.valid_raws), len(self.raws))
        for raw_key, raw in self.raws.items():
            msg += "    <%s[D%s]: %s>\n" \
                   % (raw_key, raw.deleted, raw.source_path)
        msg += "  <products: %d [%d]>\n" % (len(self.valid_products), len(self.products))
        for product_key, product in self.products.items():
            msg += "    <%s[D%s]: %s>\n" \
                   % (product_key, product.deleted, product.source_path)
        return msg
