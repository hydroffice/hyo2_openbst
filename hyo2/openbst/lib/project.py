import logging
from netCDF4 import Dataset, Group, num2date
from pathlib import Path
import shutil

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress
# noinspection PyUnresolvedReferences

from hyo2.openbst.lib import lib_info
from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.project_info import ProjectInfo
from hyo2.openbst.lib.processing.process import Process
from hyo2.openbst.lib.processing.parameters import Parameters
from hyo2.openbst.lib.raw.raws import Raws
logger = logging.getLogger(__name__)


class Project:

    ext = ".openbst"

    def __init__(self, prj_path: Path, force_prj_creation: bool = False,
                 progress: AbstractProgress = CliProgress(use_logger=True)):

        # check extension for passed project path
        if prj_path.suffix != self.ext:
            raise RuntimeError("invalid project extension: %s" % prj_path)

        # delete project if force variable is true
        if force_prj_creation is True:
            if prj_path.exists() is True:
                shutil.rmtree(str(prj_path))

        prj_path.mkdir(parents=True, exist_ok=True)

        self._path = prj_path
        _ = self.raws_folder
        _ = self.process_folder
        _ = self.products_folder

        self.progress = progress

        self._i = ProjectInfo(prj_path=self._path)
        self._r = Raws(raws_path=self.raws_folder)
        self._p = Process(process_path=self.process_folder, parent_process=self.info.process_group.parent_process)
        self._healthy = False
        self.check_health()

        self.parameters = Parameters()

    @property
    def healthy(self) -> bool:
        return self._healthy

    @healthy.setter
    def healthy(self, value: bool) -> None:
        self._healthy = value

    @property
    def name(self) -> str:
        return self._path.stem

    @property
    def path(self) -> Path:
        return self._path

    @property
    def raws_folder(self) -> Path:
        path = self._path.joinpath("raws")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def process_folder(self) -> Path:
        path = self._path.joinpath("process")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def products_folder(self) -> Path:
        path = self._path.joinpath("products")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def info(self) -> ProjectInfo:
        return self._i

    @property
    def raws(self) -> Raws:
        return self._r

    @property
    def process(self) -> Process:
        return self._p

    def open_project_folder(self) -> None:
        Helper.explore_folder(str(self.path))

    # ### RAWS ###

    def add_raw(self, path: Path) -> bool:
        self.progress.start(title="Reading", text="Ongoing reading. Please wait!",
                            init_value=10)

        added = self.info.add_raw(path=path)
        if not added:
            self.progress.end()
            return False
        self.progress.update(33)

        added = self.raws.add_raw(path=path)
        if not added:
            self.progress.end()
            return False
        self.progress.update(66)

        added = self.process.add_raw_process(path=path)
        if not added:
            self.progress.end()
            return False
        self.progress.update(99)

        self.healthy = False
        self.progress.end()
        return True

    def remove_raw(self, path: Path) -> bool:
        self.progress.start(title="Deleting", text="Ongoing deleting. Please wait!",
                            init_value=10)

        removed = self.info.remove_raw(path=path)
        if not removed:
            self.progress.end()
        self.progress.update(33)

        removed = self.raws.remove_raw(path=path)
        if not removed:
            self.progress.end()
            return False
        self.progress.update(66)

        removed = self.process.remove_raw_process(path=path)
        if not removed:
            self.progress.end()
            return False
        self.progress.update(99)

        self.progress.end()
        return True

    def check_health(self) -> None:
        self.progress.start(title="Checking Project Health", text="Ongoing file validation. Please wait!",
                            init_value=10)

        for path_hash in self.info.raws.keys():
            raw_file_log = self.info.raws[path_hash]

            if raw_file_log.deleted == 1:
                if path_hash in self.raws.raws_list:
                    raw_nc_path = self.raws.path.joinpath(path_hash + self.raws.ext)
                    self.remove_raw(raw_nc_path)
                continue

            if raw_file_log.linked == 1:
                raw_source_path = Path(raw_file_log.source_path)
                if not raw_source_path.exists():
                    raw_file_log.linked = 0

            if raw_file_log.imported == 0:
                if raw_file_log.linked == 0:
                    logger.warning("raw file not found: %s" % raw_file_log.source_path)
                    continue
                imported = self.raws.import_raw(path=Path(raw_file_log.source_path))
                if imported:
                    raw_file_log.imported = 1

                continue

        self.info.updated()
        self.healthy = True
        self.progress.update(self.progress.range)
        self.progress.end()
        logger.info("project status is healthy")

    def relink_raws(self):
        pass                    # TODO: Write a relink method to find source files

    def info_str(self):
        txt = str()
        txt += "  <name: %s>\n" % self.name
        txt += "  <path: %s>\n" % self.path
        txt += "  <raws: %d>\n" % len(self.info.valid_raws)
        return txt

    # ### Process ###
    def raw_decode(self):
        for path_hash in self.raws.raws_list:
            raw_file_path = self.raws_folder.joinpath(path_hash + self.raws.ext)
            process_file_path = self.process_folder.joinpath(path_hash + self.process.ext)

            processed = self.process.run_process(process_method=self.process.process_method_types.RAWDECODE,
                                                 process_file_path=process_file_path,
                                                 raw_path=raw_file_path,
                                                 parameters=self.parameters)
            if processed is True:
                self.info.manage_parent(parent=self.process.proc_manager.parent_process)
                print('File Raw Decoded: %s' % process_file_path.resolve())

    def static_gain_correction(self):
        for path_hash in self.raws.raws_list:
            raw_file_path = self.raws_folder.joinpath(path_hash + self.raws.ext)
            process_file_path = self.process_folder.joinpath(path_hash + self.process.ext)

            processed = self.process.run_process(process_method=self.process.process_method_types.STATICGAIN,
                                                 process_file_path=process_file_path,
                                                 raw_path=raw_file_path,
                                                 parameters=self.parameters)
            if processed is True:
                self.info.manage_parent(parent=self.process.proc_manager.parent_process)
                print('File Corrected for static gain: %s' % process_file_path.resolve())

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__
        msg += self.info_str()
        return msg
