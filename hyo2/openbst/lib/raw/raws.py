import glob
import logging
import os

from netCDF4 import Dataset
from ogr import osr
from pathlib import Path

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.raw.raw_formats import RawFormatType

from hyo2.openbst.lib.raw.parsers.reson.imports import RawImport as reson_import
from hyo2.openbst.lib.raw.parsers.reson.reader import Reson

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
        imported = False
        raw_format = RawFormatType.retrieve_format_type(path=path)

        # Open raw nc
        path_hash = NetCDFHelper.hash_string(str(path))
        if path_hash not in self.raws_list:
            raise LookupError("raw nc file not found: %s" % path)
        else:
            file_name = self.path.joinpath(path_hash + self.ext)
            ds_raw = Dataset(filename=file_name, mode='a')

        # generate raw parser object
        if raw_format is RawFormatType.KNG_ALL:
            pass                                                    # TODO: Create the Kongsberg parser

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
            imported = reson_import.import_raw(raw=raw, ds=ds_raw)
            raw.close()

        elif raw_format is RawFormatType.RESON_7K:
            raw = Reson(path)
            if raw.valid is True:
                raw.data_map()
            else:
                return False
            imported = reson_import.import_raw(raw=raw, ds=ds_raw)
            raw.close()

        elif raw_format is RawFormatType.R2SONIC_S7K:
            pass                                                      # TODO: Create R2Sonic Parser

        if imported is False:
            raise RuntimeError(" Error Importing file: %s" % path)

        ds_raw.close()
        logger.info("Imported file into project: %s" % path)
        return True
