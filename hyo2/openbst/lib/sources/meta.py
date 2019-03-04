import logging
from typing import Optional

from hyo2.abc.lib.gdal_aux import GdalAux
from PySide2 import QtCore

logger = logging.getLogger(__name__)


class Meta:

    def __init__(self):
        self.settings = QtCore.QSettings()

        self._has_spatial_info = False

        self._crs = None
        self._gt = None

        self._x_min = None
        self._x_max = None
        self._x_res = None
        self._y_min = None
        self._y_max = None
        self._y_res = None

    @property
    def has_spatial_info(self) -> bool:
        return self._has_spatial_info

    @has_spatial_info.setter
    def has_spatial_info(self, value: bool) -> None:
        self._has_spatial_info = value

    @property
    def crs(self) -> Optional[str]:
        return self._crs

    @crs.setter
    def crs(self, value: str) -> None:
        self._crs = value

    @property
    def gt(self):
        return self._gt

    @gt.setter
    def gt(self, value) -> None:
        self._gt = value

    @property
    def crs_id(self) -> Optional[str]:
        if self._crs is None:
            return None
        return GdalAux.crs_id(self._crs)

    @property
    def x_min(self) -> Optional[float]:
        return self._x_min

    @x_min.setter
    def x_min(self, value) -> None:
        self._x_min = value

    @property
    def x_max(self) -> Optional[float]:
        return self._x_max

    @x_max.setter
    def x_max(self, value) -> None:
        self._x_max = value

    @property
    def x_res(self) -> Optional[float]:
        return self._x_res

    @x_res.setter
    def x_res(self, value) -> None:
        self._x_res = value

    @property
    def y_min(self) -> Optional[float]:
        return self._y_min

    @y_min.setter
    def y_min(self, value) -> None:
        self._y_min = value

    @property
    def y_max(self) -> Optional[float]:
        return self._y_max

    @y_max.setter
    def y_max(self, value) -> None:
        self._y_max = value

    @property
    def y_res(self) -> Optional[float]:
        return self._y_res

    @y_res.setter
    def y_res(self, value) -> None:
        self._y_res = value

    # ### OTHER ###

    def str_info(self) -> str:
        msg = str()

        msg += "- has spatial info: %s\n" % self._has_spatial_info
        msg += "- gt: %s\n" % (self._gt, )
        if len(self._crs) > 34:
            msg += "- crs: '%s[...]' -> [%s]\n" % (self._crs[:30], self.crs_id)
        else:
            msg += "- crs: '%s' -> [%s]\n" % (self._crs, self.crs_id)
        msg += "- x: %s %s %s\n" % (self._x_min, self._x_max, self._x_res)
        msg += "- y: %s %s %s\n" % (self._y_min, self._y_max, self._y_res)

        return msg

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <has spatial info: %s>\n" % self._has_spatial_info
        msg += "  <gt: %s>\n" % (self._gt, )
        msg += "  <crs: %s[%s]>\n" % (self._crs, self.crs_id)
        msg += "  <x: %s %s %s>\n" % (self._x_min, self._x_max, self._x_res)
        msg += "  <y: %s %s %s>\n" % (self._y_min, self._y_max, self._y_res)

        return msg
