import logging
from pathlib import Path
from typing import Optional

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress

from hyo2.openbst.lib import lib_info
from hyo2.openbst.lib.setup import Setup
from hyo2.openbst.lib.project import Project

logger = logging.getLogger(__name__)


class OpenBST:

    def __init__(self, prj_name: str = "default", setup_name: str = "default", force_new: bool = False,
                 progress: AbstractProgress = CliProgress(use_logger=True)) -> None:

        self.progress = progress

        self._setup = Setup(name=setup_name, prj_name=prj_name, setups_folder=self.setups_folder())
        cur_proj_path = self.projects_folder().joinpath(self._setup.current_project + Project.ext)
        self._prj = Project(prj_path=cur_proj_path, force_prj_creation=force_new,
                            progress=self.progress)

    # ### ROOT FOLDER ###

    @classmethod
    def root_folder(cls) -> Path:
        root_folder = Path(Helper(lib_info=lib_info).package_folder())
        if not root_folder.exists():
            root_folder.mkdir(parents=True, exist_ok=True)
        return root_folder

    def open_root_folder(self) -> None:
        Helper.explore_folder(str(self.root_folder()))

    # ### SETUPS ###

    @classmethod
    def setups_folder(cls) -> Path:
        folder = cls.root_folder().joinpath("setups")
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    @property
    def setups_list(self) -> list:
        """This list may be used in a future to change the current setup"""
        return [path.stem for path in self.setups_folder().glob("*%s" % Setup.ext)]

    @property
    def setup(self) -> Setup:
        return self._setup

    # ### project ###

    @classmethod
    def projects_folder(cls) -> Path:
        folder = cls.root_folder().joinpath("projects")
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    @property
    def projects_list(self) -> list:
        return [path.stem for path in self.projects_folder().iterdir() if path.suffix == Project.ext]

    @property
    def prj(self) -> Project:
        return self._prj

    def open_projects_folder(self) -> None:
        Helper.explore_folder(str(self.projects_folder()))

    # ### OTHER ###

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <root folder: %s>\n" % self.root_folder()
        msg += "  <setups: %d>\n" % len(self.setups_list)
        msg += "  <projects: %d>\n" % len(self.projects_list)
        msg += "  <current setup: %s>\n" % self.setup.path
        msg += "  <current project: %s>\n" % self.prj.path

        return msg
