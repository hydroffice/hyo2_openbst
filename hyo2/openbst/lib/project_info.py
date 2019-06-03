from datetime import datetime
import logging
from pathlib import Path
from netCDF4 import Dataset, Group, num2date

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


class ProjectInfo:

    def __init__(self, prj_path: Path) -> None:
        self._path = prj_path.joinpath("info.nc")
        self._i = None
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
        return self._i.Conventions

    @property
    def time_units(self) -> str:
        return self._i.variables["time"].units

    @property
    def time_calendar(self) -> str:
        return self._i.variables["time"].calendar

    @property
    def version(self) -> str:
        return self._i.version

    @property
    def created(self) -> datetime:
        return num2date(self._i.created, units=self.time_units, calendar=self.time_calendar)

    @property
    def modified(self):
        return num2date(self._i.modified, units=self.time_units, calendar=self.time_calendar)

    @property
    def raws_group(self) -> Group:
        return self._i.groups[self._raws_name]

    @property
    def raws(self):
        return self.raws_group.variables

    @property
    def valid_raws(self) -> list:
        valid_raws = list()
        for raw_key, raw in self.raws.items():
            if raw.deleted == 0:
                valid_raws.append(raw_key)
        return valid_raws

    @property
    def products_group(self) -> Group:
        return self._i.groups[self._products_name]

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
        self._i = Dataset(filename=self._path, mode=open_mode)

        NetCDFHelper.init(ds=self._i)
        # logger.debug("conventions: %s" % self.conventions)
        # logger.debug("time: %s [%s]" % (self.time_units, self.time_calendar))
        # logger.debug("version: %s" % self.version)
        # logger.debug("created: %s" % self.created)
        # logger.debug("modified: %s" % self.modified)

        NetCDFHelper.groups(ds=self._i, names=[self._raws_name, self._products_name])

        logger.info("open in '%s' mode: [v.%s] %s" % (open_mode, self.version, self.path))

    def updated(self):
        NetCDFHelper.update_modified(self._i)

    # # ### RAWS ###

    def add_raw(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("The source does not exist: %s" % path)
            return False

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.raws.keys():
            try:
                if self.raws[path_hash].deleted == 1:
                    self.raws[path_hash].deleted = 0
                    logger.info("Raw entry was deleted: %s" % path)
            except AttributeError:
                self.raws[path_hash].deleted = 0
        else:
            path_var = self.raws_group.createVariable(path_hash, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            logger.debug("Raw entry was added: %s" % path)

        return True

    def remove_raw(self, path: Path) -> bool:

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raws.keys():
            logger.info("File already removed: %s" % path)
            return False

        self.raws[path_hash].deleted = 1
        logger.debug("removed: %s" % path)
        return True

    # # ### PRODUCTS ###

    def add_product(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("The product does not exist: %s" % path)
            return False

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.products.keys():
            try:
                if self.products[path_hash].deleted == 1:
                    self.products[path_hash].deleted = 0
                    logger.info("Product entry was deleted: %s" % path)
            except AttributeError:
                self.products[path_hash].deleted = 0
        else:
            path_var = self.products_group.createVariable(path_hash, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            logger.debug("Raw entry was added: %s" % path)

        return True

    def remove_product(self, path: Path) -> bool:

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.products.keys():
            logger.info("File already removed: %s" % path)
            return False

        self.products[path_hash].deleted = 1
        logger.debug("removed: %s" % path)
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
