from datetime import datetime
import logging
from pathlib import Path
from netCDF4 import Dataset, num2date

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


class Setup:
    """OpenBST Setup"""

    ext = ".nc"

    def __init__(self, name: str, prj_name: str, setups_folder: Path) -> None:

        self._setup_name = self.make_setup_name(name)
        self._setups_folder = setups_folder
        self._path = self.make_setup_path(setups_folder=self._setups_folder,
                                          setup_name=name)
        self._prj_name = prj_name
        self._ds = None
        self._time = None
        self._nc()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._path.name.replace(self.ext, "")

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

        self._ds = Dataset(filename=self._path, mode=open_mode)

        NetCDFHelper.init(ds=self._ds)
        # logger.debug("conventions: %s" % self.conventions)
        # logger.debug("time: %s [%s]" % (self.time_units, self.time_calendar))
        # logger.debug("version: %s" % self.version)
        # logger.debug("created: %s" % self.created)
        # logger.debug("modified: %s" % self.modified)

        # current project
        self.current_project = self._prj_name

        logger.info("open in '%s' mode: [v.%s] %s" % (open_mode, self.version, self.path))

    def updated(self):
        NetCDFHelper.update_modified(self._ds)

    @classmethod
    def make_setup_name(cls, setup_name: str) -> str:
        if setup_name is None:
            return "default"
        setup_name = setup_name.replace(" ", "_")
        return setup_name

    @classmethod
    def make_setup_path(cls, setups_folder: Path, setup_name: str) -> Path:
        setup_path = setups_folder.joinpath(setup_name + cls.ext)
        return setup_path

    @classmethod
    def list_setup_names(cls, root_folder) -> list:
        names_list = list()
        for path in root_folder.rglob("*.setup"):
            if path.is_file():
                names_list.append(path.name.replace(".setup", ""))
        return names_list

    # ### CURRENT PROJECT ###

    @property
    def current_project(self) -> str:
        return self._ds.current_project

    @current_project.setter
    def current_project(self, current_project: str) -> None:
        self._ds.current_project = current_project
        self.updated()

    # ### OTHER ###

    def info_str(self) -> str:
        txt = str()
        txt += "  <name: %s>\n" % self.name
        txt += "  <setups folder: %s>\n" % self._setups_folder
        txt += "  <version: %s>\n" % self.version
        txt += "  <created: %s>\n" % self.created
        txt += "  <modified: %s>\n" % self.modified
        txt += "  <current project: %s>\n" % self.current_project
        return txt

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__
        msg += self.info_str()
        return msg
