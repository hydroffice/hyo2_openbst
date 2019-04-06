import logging
import os
from typing import Optional
from netCDF4 import Dataset

from hyo2.abc.lib.helper import Helper
from hyo2.openbst.lib import lib_info

logger = logging.getLogger(__name__)


class Setup:
    """OpenBST Setup"""

    def __init__(self, setup_name: str, root_folder: str) -> None:

        self._root_folder = root_folder
        self._setup_name = self.make_setup_name(setup_name)
        self._setups_folder = self.make_setups_folder(root_folder=root_folder)
        self._setup_path = self.make_setup_path(setups_folder=self._setups_folder,
                                                setup_name=setup_name)
        self._setup = None
        self._make_netcdf()

    def _make_netcdf(self):
        open_mode = "w"
        if os.path.exists(self._setup_path):
            open_mode = "a"

        self._setup = Dataset(filename=self._setup_path, mode=open_mode)
        logger.debug("open in '%s' mode: [%s] %s" % (open_mode, self._setup.data_model, self._setup_path))

        if open_mode == "w":
            self._setup.version = lib_info.lib_version
            self._setup.projects_folder = self._default_projects_folder()
            self._setup.outputs_folder = self._default_outputs_folder()

        else:
            if self._setup.version > lib_info.lib_version:
                raise RuntimeError("Setup has a future version: %s" % self.setup_version)

        logger.debug("setup version: %s" % self._setup.version)

    @classmethod
    def make_setup_name(cls, setup_name: str) -> str:
        if setup_name is None:
            return "default"
        setup_name = setup_name.replace(" ", "_")
        return setup_name

    @classmethod
    def make_setups_folder(cls, root_folder: str) -> str:
        setups_folder = os.path.join(root_folder, "setups")
        if not os.path.exists(setups_folder):
            os.makedirs(setups_folder)
        return setups_folder

    @classmethod
    def make_setup_path(cls, setups_folder: str, setup_name: str) -> str:
        setup_path = os.path.join(setups_folder, setup_name + ".setup")
        return setup_path

    @property
    def setup_name(self) -> str:
        return self._setup_name

    @property
    def setups_folder(self) -> str:
        return self._setups_folder

    @property
    def setup_path(self) -> str:
        return self._setup_path

    @property
    def setup_version(self) -> str:
        return self._setup.version

    def open_setups_folder(self) -> None:
        Helper.explore_folder(self._setups_folder)

    # ### PROJECTS FOLDER ###

    def _default_projects_folder(self) -> str:
        projects_folder = os.path.join(self._root_folder, "projects")
        if not os.path.exists(projects_folder):
            os.makedirs(projects_folder)
        return projects_folder

    @property
    def projects_folder(self) -> str:
        return self._setup.projects_folder

    @projects_folder.setter
    def projects_folder(self, projects_folder: str) -> None:
        if not os.path.exists(projects_folder):
            raise RuntimeError("the passed projects folder does not exist: %s"
                               % projects_folder)
        self._setup.projects_folder = projects_folder

    def open_projects_folder(self) -> None:
        Helper.explore_folder(self.projects_folder)

    # ### OUTPUTS FOLDER ###

    def _default_outputs_folder(self) -> str:
        outputs_folder = os.path.join(self._root_folder, "outputs")
        if not os.path.exists(outputs_folder):
            os.makedirs(outputs_folder)
        return outputs_folder

    @property
    def outputs_folder(self) -> str:
        return self._setup.outputs_folder

    @outputs_folder.setter
    def outputs_folder(self, outputs_folder: str) -> None:
        if not os.path.exists(outputs_folder):
            raise RuntimeError("the passed outputs folder does not exist: %s"
                               % outputs_folder)
        self._setup.outputs_folder = outputs_folder

    def open_outputs_folder(self) -> None:
        Helper.explore_folder(self.outputs_folder)

    # ### OTHER ###

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <path: %s>\n" % self.setup_path
        msg += "  <version: %s>\n" % self.setup_version
        msg += "  <projects folder: %s>\n" % self.projects_folder
        msg += "  <outputs folder: %s>\n" % self.outputs_folder
        return msg
