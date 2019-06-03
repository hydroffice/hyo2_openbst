import logging
import os
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

    def __init__(self, setup_name: str = "default",
                 progress: AbstractProgress = CliProgress(use_logger=True)) -> None:

        self.progress = progress

        self._setup = Setup(name=setup_name, root_folder=self.root_folder())
        self._cur_projs = self._setup.root_folder.joinpath("projects")
        self._cur_projs.mkdir(parents=True, exist_ok=True)
        cur_proj_path = self._cur_projs.joinpath(self._setup.current_project + Project.ext)
        self._prj = Project(prj_path=cur_proj_path, progress=self.progress)

    # ### ROOT FOLDER ###

    @classmethod
    def root_folder(cls) -> Path:
        root_folder = Path(Helper(lib_info=lib_info).package_folder())
        if not root_folder.exists():
            root_folder.mkdir(parents=True, exist_ok=True)
        return root_folder

    def open_root_folder(self) -> None:
        Helper.explore_folder(str(self.root_folder()))

    # ### SETUP ###

    @property
    def setup(self) -> Setup:
        return self._setup

    # ### project ###

    @property
    def prj(self) -> Project:
        return self._prj

    # ### OTHER ###

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <root folder: %s>\n" % self.root_folder()
        msg += "  <setup: %s>\n" % self.setup.path
        msg += "  <project: %s>\n" % self.prj.path

        return msg
