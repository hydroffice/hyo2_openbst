import glob
import logging
import os

from collections import OrderedDict
from netCDF4 import Dataset, Group, Variable, num2date
from ogr import osr
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.raw.raw_formats import RawFormatType

from hyo2.openbst.lib.raw.reson import Reson
logger = logging.getLogger(__name__)


class Raws:

    ext = ".nc"

    def __init__(self, raws_path: Path) -> None:
        self._path = raws_path

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

    # common project management methods
    def add_raw(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash in self.raws_list:
            logger.info("file already in project: %s" % path)
        else:
            file_name = self.path.joinpath(path_hash + self.ext)
            raw = Dataset(filename=file_name, mode='w')
            NetCDFHelper.init(ds=raw)
            raw.close()
            logger.info("raw .nc created for added file: %s" % str(path.resolve()))
        return True

    def remove_raw(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raws_list:
            logger.info("absent: %s" % path)
            return False
        else:
            raw_path = self._path.joinpath(path_hash + Raws.ext)
            os.remove(str(raw_path.resolve()))
            logger.info("raw .nc deleted for file: %s" % str(path.resolve()))
            return True

    # class specific methods
    def import_raw(self, path: Path) -> bool:
        raw_format = RawFormatType.retrieve_format_type(path=path)
        raw = None

        if raw_format is RawFormatType.KNG_ALL:
            pass                                                        # TODO: Create the Kongsberg parser
        elif raw_format is RawFormatType.KNG_KMALL:
            pass
        elif raw_format is RawFormatType.KNG_WCD:
            pass
        elif raw_format is RawFormatType.RESON_S7K:
            raw = Reson(path)
            if raw.valid is True:
                raw.data_map()
            else:
                return False
        elif raw_format is RawFormatType.RESON_7K:
            raw = Reson(path)
            if raw.valid is True:
                raw.data_map()
            else:
                return False
        elif raw_format is RawFormatType.R2SONIC_S7K:
            pass                                                      # TODO: Create R2Sonic Parser

        # Open raw nc
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raws_list:
            raise LookupError("raw nc file not found: %s" % path)
        else:
            file_name = self.path.joinpath(path_hash + self.ext)
            ds_raw = Dataset(filename=file_name, mode='a')

        # Get position
        Raws.get_position(raw=raw, ds=ds_raw)

    @staticmethod
    def get_position(raw: Reson, ds: Dataset) -> None:
        times, lat, lon = raw.get_position()

        grp_pos = ds.createGroup("Position")
        grp_pos.createDimension(dimname="time", size=None)
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromEPSG(4326)
        grp_pos.spatial_ref = spatial_reference

        var_time = grp_pos.createVariable(varname="time", datatype="f8", dimensions=("time",))
        var_time[:] = times
        var_lat = grp_pos.createVariable(varname="latitude", datatype="f8", dimensions=("time",))
        var_lat[:] = lat
        var_lon = grp_pos.createVariable(varname="longitude", datatype="f8", dimensions=("time",))
        var_lon[:] = lon

        NetCDFHelper.update_modified(ds=ds)
        return

    @staticmethod
    def get_attitude(raw: Reson, ds: Dataset):
        times, pitch, roll, heave, yaw = raw.get_attitude()

        grp_attitude = ds.createGroup("Attitude")
        grp_attitude.createDimension(dimname="time", size=None)

