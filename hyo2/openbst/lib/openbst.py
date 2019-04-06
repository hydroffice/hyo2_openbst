import logging
import os
from typing import Optional

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress

from hyo2.openbst.lib import lib_info
from hyo2.openbst.lib.setup import Setup
from hyo2.openbst.lib.project import Project

logger = logging.getLogger(__name__)


class OpenBST:

    def __init__(self,
                 setup_name: Optional[str] = None,
                 progress: AbstractProgress = CliProgress(use_logger=True)) -> None:

        self.progress = progress

        self._setup = Setup(setup_name=setup_name, root_folder=self.root_folder())
        self._prj = Project(prj_path=self._setup.current_project, progress=self.progress)

    # ### ROOT FOLDER ###

    @classmethod
    def root_folder(cls) -> str:
        root_folder = Helper(lib_info=lib_info).package_folder()
        if not os.path.exists(root_folder):
            os.makedirs(root_folder)
        return root_folder

    def open_root_folder(self) -> None:
        Helper.explore_folder(self.root_folder())

    # ### SETUP ###

    @property
    def setup(self) -> Setup:
        return self._setup

    # ### project ###

    @property
    def project(self) -> Project:
        return self._prj

    # ### OTHER ###

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <root folder: %s>\n" % self.root_folder()
        msg += "  <setup: %s>\n" % self._setup.setup_path
        msg += "  <project: %s>\n" % self._prj.project_info_path

        return msg
