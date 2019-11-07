import glob
import logging
import os

from collections import OrderedDict
from netCDF4 import Dataset, Group, Variable, num2date
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


class Raws:

    ext = ".nc"

    def __init__(self, raws_path: Path) -> None:
        self._path = raws_path
        self._validated = False

    @property
    def validated(self) -> bool:
        return self._validated

    @validated.setter
    def validated(self, value: bool) -> None:
        self._validated = value

    @property
    def path(self) -> Path:
        return self._path

    @property
    def raws_list(self) -> list:
        raw_list = list()
        for hash_file in glob.glob(str(self._path.joinpath("*" + Raws.ext))):
            hash_path = Path(hash_file)
            raw_list.append(hash_path.name.split('.')[0])
        return raw_list

    def add_raw(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.raws_list:
            logger.info("file already in project: %s" % path)
        else:
            file_name = self.path.joinpath(path_hash + self.ext)
            raw = Dataset(filename=file_name, mode='w')
            NetCDFHelper.init(ds=raw)
            raw.close()
            logger.info(".nc created for added file: %s" % str(path.resolve()))
        return True

    def remove_raw(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raws_list:
            logger.info("absent: %s" % path)
            return False
        else:
            raw_path = self._r_list[path_hash]
            os.remove(str(raw_path.resolve()))
            self.raws_list = self.create_raw_list(self._path)
            logger.info(".nc deleted for file: %s" % str(path.resolve()))
            return True

    def validate_raw(self, path: Path) -> bool:
        pass

    @classmethod
    def create_raw_list(cls, raws_path: Path) -> OrderedDict:
        raw_list = OrderedDict()
        for hash_file in glob.glob(str(raws_path.joinpath("*" + Raws.ext))):
            hash_path = Path(hash_file)

            raw_list[hash_path.name.split('.')[0]] = Dataset(filename=hash_path, mode='a')

        return raw_list

