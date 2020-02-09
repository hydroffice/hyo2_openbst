from datetime import datetime
import hashlib
import logging
from netCDF4 import Dataset, Group, date2num
import numpy as np

from typing import Union

from hyo2.openbst.lib import lib_info

logger = logging.getLogger(__name__)


class NetCDFHelper:
    t_units = 'milliseconds since 1970-01-01T00:00:00'
    t_calendar = 'gregorian'

    @classmethod
    def init(cls, ds: Dataset) -> bool:

        # CF convention
        try:
            _ = ds.Conventions
        except AttributeError:
            cf = 'CF-1.6'
            ds.Conventions = cf

        # time coordinate
        try:
            _ = ds.variables["time"]
        except KeyError:
            tdim = ds.createDimension('time', None)
            time = ds.createVariable('time', np.float64, (tdim.name,))
            time.units = NetCDFHelper.t_units
            time.calendar = NetCDFHelper.t_calendar

        # version
        try:
            version = ds.version
            if version > lib_info.lib_version:
                raise RuntimeError("Project has a future version: %s" % version)
            if version < lib_info.lib_version:
                raise RuntimeError("Project has a past version: %s" % version)
        except AttributeError:
            ds.version = lib_info.lib_version

        # created
        try:
            _ = ds.created
        except AttributeError:
            ds.created = date2num(datetime.utcnow(),
                                  ds.variables["time"].units, ds.variables["time"].calendar)

        # modified
        try:
            _ = ds.modified
        except AttributeError:
            ds.modified = date2num(datetime.utcnow(),
                                   ds.variables["time"].units, ds.variables["time"].calendar)

        ds.sync()

        return True

    @classmethod
    def groups(cls, ds: Union[Dataset, Group], names: list) -> bool:

        for name in names:

            try:
                _ = ds.groups[name]

            except KeyError:
                ds.createGroup(name)

        ds.sync()

        return True

    @classmethod
    def update_modified(cls, ds: Dataset) -> bool:

        ds.modified = date2num(datetime.utcnow(),
                               ds.variables["time"].units, ds.variables["time"].calendar)

        ds.sync()

        return True

    @classmethod
    def hash_string(cls, input_str: str) -> str:
        return hashlib.sha256(input_str.encode('utf-8')).hexdigest()
