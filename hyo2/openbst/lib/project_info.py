import logging
import os
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
        self._process_name = "process"
        self._products_name = "products"
        self._supplementals_name = "supplemental_files"
        self._ssp_name = "sound_speed_profiles"
        self._calibration_name = "calibration_files"
        self._nc()
        self.manage_parent()

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
    def supplemental_group(self):
        return self._ds.groups[self._supplementals_name]

    @property
    def ssp_group(self):
        return self.supplemental_group.groups[self._ssp_name]

    @property
    def ssps(self):
        return self.ssp_group.variables

    @property
    def ssp_list(self) -> list:
        ssp_list = list()
        for ssp_name, ssp in self.ssps.items():
            if ssp.deleted == 0:
                ssp_list.append(ssp_name)
        return ssp_list

    @property
    def calibration_group(self):
        return self.supplemental_group.groups[self._calibration_name]

    @property
    def calibrations(self):
        return self.calibration_group.variables

    @property
    def calibration_list(self) -> list:
        calibration_list = list()
        for calib_name, calibration in self.calibrations.items():
            if calibration.deleted == 0:
                calibration_list.append(calib_name)
        return calibration_list

    @property
    def process_group(self) -> Group:
        return self._ds.groups[self._process_name]

    @property
    def processes(self):
        return self.process_group.variables

    @property
    def project_process(self):
        project_processes = list()
        for process_key, process in self.processes.items():
            if process.deleted == 0:
                project_processes.append(process_key)
        return project_processes

    @property
    def products_group(self) -> Group:
        return self._ds.groups[self._products_name]

    @property
    def products(self):
        return self.products_group.variables

    @property
    def project_products(self) -> list:
        project_products = list()
        for product_key, product in self.products.items():
            if product.deleted == 0:
                project_products.append(product_key)
        return project_products

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

        NetCDFHelper.groups(ds=self._ds, names=[self._raws_name, self._process_name, self._products_name,
                                                self._supplementals_name])
        grp_supplements = self._ds.groups[self._supplementals_name]
        NetCDFHelper.groups(ds=grp_supplements, names=[self._ssp_name, self._calibration_name])

        logger.info("open in '%s' mode: [v.%s] %s" % (open_mode, self.version, self.path))

    def updated(self):
        NetCDFHelper.update_modified(self._ds)

    def remove_nc_file(self):
        if self._ds:
            self._ds.close()
            self._ds = None
            if self._path.exists():
                os.remove(str(self._path.resolve()))

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

    # # ### Supplemental Files ### # #
    def add_ssp(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("path does not exist: %s" % path)
            return False

        if path.suffix != '.csv':
            logger.warning("invalid extension: %s" % path)
            return False
        if path.stem in self.ssps.keys():
            try:
                if self.ssps[path.stem].deleted == 1:
                    self.ssps[path.stem].deleted = 0
                    logger.info("previously deleted: %s" % path)
            except AttributeError:
                self.ssps[path.stem].deleted = 0
        else:
            path_var = self.ssp_group.createVariable(path.stem, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            logger.debug("added: %s" % path)

        self._ds.sync()
        return True

    def remove_ssp(self, path: Path) -> bool:
        if path.stem not in self.ssps.keys():
            logger.info("absent: %s" % path)
            return False

        self.ssps[path.stem].deleted = 1
        logger.debug("removed: %s" % path)

        self._ds.sync()
        return True

    def add_calibration(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("path does not exist: %s" % path)
            return False

        if path.suffix != '.csv':
            logger.warning("invalid extension: %s" % path)
            return False

        if path.stem in self.calibrations.keys():
            try:
                if self.calibrations[path.stem].deleted == 1:
                    self.calibrations[path.stem].deleted = 0
                    logger.info("previously deleted: %s" % path)
            except AttributeError:
                self.calibrations[path.stem].deleted = 0
        else:
            path_var = self.calibration_group.createVariable(path.stem, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            logger.debug("added: %s" % path)
        self._ds.sync()
        return True

    def remove_calibration(self, path: Path) -> bool:
        if path.stem not in self.calibrations.keys():
            logger.info("absent: %s" % path)
            return False

        self.calibrations[path.stem].deleted = 1
        logger.debug("removed: %s" % path)
        self._ds.sync()
        return True

    # # ### PROCESSES ### # #
    def manage_parent(self, parent=None):
        if parent is None:
            try:
                _ = self.process_group.parent_process
            except AttributeError:
                self.process_group.parent_process = ''
        else:
            self.process_group.parent_process = parent
        self.updated()

    def add_process(self, path: Path) -> bool:
        path = path.resolve()
        if not path.exists():
            logger.warning("does not exist: %s" % path)
            return False

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.processes.keys():
            try:
                if self.processes[path_hash].deleted == 1:
                    self.processes[path_hash].deleted = 0
                    logger.info("previously deleted: %s" % path)
            except AttributeError:
                self.processes[path_hash].deleted = 0
        else:
            path_var = self.process_group.createVariable(path_hash, 'u1')
            path_var.source_path = str(path)
            path_var.deleted = 0
            logger.debug("added: %s" % path)

        self._ds.sync()
        return True

    def remove_process(self, path: Path) -> bool:

        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.processes.keys():
            logger.info("absent: %s" % path)
            return False

        self.processes[path_hash].deleted = 1
        logger.debug("removed: %s" % path)

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
