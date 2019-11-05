import logging
from netCDF4 import Dataset, Group, Variable, num2date
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper
logger = logging.getLogger(__name__)

class Raws:

    ext = ".nc"

    def __init__(self, raws_path: Path) -> None:
        self._path = raws_path
        self.raws_list = None

    @property
    def path(self) -> Path:
        return self._path

    def add_raw(self,path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        raw = Dataset(filename=self.path.joinpath(path_hash + self.ext), mode=)
