from copy import deepcopy
from collections import deque
from enum import Enum
import logging
import math
import random
from typing import Optional

import numpy as np
from scipy import ndimage
from PySide2 import QtCore

from hyo2.openbst.lib.sources.meta import Meta
from hyo2.openbst.lib.sources.format import FormatType
from hyo2.openbst.lib.sources.layer_plot import LayerPlot
from hyo2.openbst.lib.sources.layer_type import LayerType

logger = logging.getLogger(__name__)


class EraseType(Enum):
    Plain = 1
    Bell = 2
    Triangle = 3
    Hill = 4


class FilterType(Enum):
    Gaussian = 1
    Median = 2


class CloneType(Enum):
    Plain = 1
    Averaged = 2
    Bell = 3
    Triangle = 4
    Noise = 5
    Hill = 6
    BellNoise = 7
    TriangleNoise = 8


class Layer:

    def __init__(self, layer_type: LayerType, format_type: FormatType):
        self.meta = Meta()
        self.settings = QtCore.QSettings()

        self._layer_type = layer_type
        self._format_type = format_type

        self._modified_after_last_save = False

        self._array = None
        self._array_min = None
        self._array_max = None

        self._features = dict()

        self._undo_arrays = deque()
        self._undo_features = deque()

        self.plot = LayerPlot(layer=self)

    @property
    def layer_type(self) -> LayerType:
        return self._layer_type

    @property
    def format_type(self) -> FormatType:
        return self._format_type

    @property
    def modified(self) -> bool:
        return self._modified_after_last_save

    @modified.setter
    def modified(self, value: bool) -> None:
        self._modified_after_last_save = value

    def is_bathymetry(self) -> bool:
        return self._layer_type == LayerType.BATHYMETRY

    def is_uncertainty(self) -> bool:
        return self._layer_type == LayerType.UNCERTAINTY

    def is_designated_soundings(self) -> bool:
        return self._layer_type == LayerType.DESIGNATED

    def is_mosaic(self) -> bool:
        return self._layer_type == LayerType.MOSAIC

    def is_raster(self) -> bool:
        return self._layer_type in [LayerType.BATHYMETRY, LayerType.UNCERTAINTY, LayerType.MOSAIC]

    def is_vector(self) -> bool:
        return self._layer_type in [LayerType.DESIGNATED, ]

    @property
    def array(self) -> Optional[np.ndarray]:
        return self._array

    @array.setter
    def array(self, value: Optional[np.ndarray]) -> None:
        self._array = value

    @property
    def array_min(self) -> float:
        if self._array is None:
            return float('nan')
        # noinspection PyTypeChecker
        return np.nanmin(self._array)

    @property
    def array_max(self) -> float:
        if self._array is None:
            return float('nan')
        # noinspection PyTypeChecker
        return np.nanmax(self._array)

    @property
    def features(self) -> dict:
        return self._features

    @property
    def features_x(self) -> list:
        xs = list()
        for feature in self._features.values():
            if feature['flagged']:
                continue
            xs.append(feature['x'])
        return xs

    @property
    def features_y(self) -> list:
        ys = list()
        for feature in self._features.values():
            if feature['flagged']:
                continue
            ys.append(feature['y'])
        return ys

    def feature_at_row_col(self, r, c, dist=1) -> Optional[dict]:
        for feature in self._features.values():
            if abs(r - feature['row']) > dist:
                continue
            if abs(c - feature['col']) > dist:
                continue
            return feature

        return None

    @features.setter
    def features(self, value: dict) -> None:
        self._features = value

    def xy2cr(self, x: float, y: float) -> tuple:
        if self.is_raster():
            if self._array is None:
                return None, None

        c = int((x - self.meta.x_min) / self.meta.x_res)
        r = int((y - self.meta.y_min) / self.meta.y_res)
        # logger.debug("c,r: %s, %s" % (c, r))

        if self.is_raster():
            if (c < 0) or (c >= self.array.shape[1]) or (r < 0) or (r >= self.array.shape[0]):
                return None, None

        return c, r

    def dcdr2dxdy(self, dc: float, dr: float) -> tuple:
        return dc * self.meta.x_res, dr * self.meta.y_res

    def cr2xy(self, c, r):
        if self.is_raster():
            if self._array is None:
                return None, None

        x = self.meta.x_min + c * self.meta.x_res
        y = self.meta.y_min + r * self.meta.y_res

        return x, y

    # ### UNDO ###

    def store_undo_array(self) -> None:
        logger.debug("storing undo array")
        if len(self._undo_arrays) >= self.settings.value("max_undo_steps", 3):
            self._undo_arrays.popleft()

        self._undo_arrays.append(np.copy(self.array))

    def store_undo_features(self) -> None:
        logger.debug("storing undo features")
        if len(self._undo_features) >= self.settings.value("max_undo_steps", 3):
            self._undo_features.popleft()

        self._undo_features.append(deepcopy(self.features))

    def undo_array_available(self) -> bool:
        return len(self._undo_arrays) != 0

    def undo_features_available(self) -> bool:
        return len(self._undo_features) != 0

    def number_of_undo_array_available(self) -> int:
        return len(self._undo_arrays)

    def number_of_undo_features_available(self) -> int:
        return len(self._undo_features)

    def undo_array(self) -> bool:
        if not self.undo_array_available():
            logger.error("undo array not available")
            return False

        logger.debug("undoing array")
        self._array = self._undo_arrays.pop()

        self.plot.updated_layer_array()

        return True

    def undo_features(self) -> bool:
        if not self.undo_features_available():
            logger.error("undo features not available")
            return False

        logger.debug("undoing features")
        self._features = self._undo_features.pop()

        return True

    # ### EDITING ###

    def shift(self, value: float) -> bool:

        self.store_undo_array()

        grid_nan = np.isnan(self._array)
        self._array += value
        self._array[grid_nan] = np.nan

        self.plot.updated_layer_array()

        self._modified_after_last_save = True
        return True

    def erase(self, pnt_x, pnt_y, sz: int = 0, use_radius: bool = False,
              erase_type: EraseType = EraseType.Plain, other_layers: Optional[list] = None) -> None:
        logger.debug("erase -> (%d, %d), size: %d, use radius: %s" % (pnt_x, pnt_y, sz, use_radius))

        pnt_c, pnt_r = self.xy2cr(x=pnt_x, y=pnt_y)
        if (pnt_c is None) or (pnt_r is None):
            return

        if other_layers is None:
            other_layers = list()
        logger.debug("erase -> nr. of other layers: %d" % (len(other_layers), ))

        if self.is_raster():
            self.store_undo_array()
        if self.is_vector():
            self.store_undo_features()

        span = sz - 1
        span_sq = span * span

        for dc in range(-span, span + 1):

            for dr in range(-span, span + 1):

                if use_radius:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    if sq > span_sq:
                        continue

                r = pnt_r + dr
                c = pnt_c + dc

                if self.is_raster():
                    if (r < 0) or (r >= self.array.shape[0]):
                        continue
                    elif (c < 0) or (c >= self.array.shape[1]):
                        continue

                    if erase_type == EraseType.Plain:

                        self.array[r, c] = np.nan
                        for other_layer in other_layers:
                            other_layer.array[r, c] = np.nan

                    elif erase_type == EraseType.Triangle:

                        sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                        dist = math.sqrt(sq)
                        o_fct = dist / span
                        rnd_value = random.uniform(0, 1)
                        if rnd_value > o_fct:
                            self.array[r, c] = np.nan
                            for other_layer in other_layers:
                                other_layer.array[r, c] = np.nan

                    elif erase_type == EraseType.Bell:

                        sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                        o_fct = sq / span_sq
                        rnd_value = random.uniform(0, 1)
                        if rnd_value > o_fct:
                            self.array[r, c] = np.nan
                            for other_layer in other_layers:
                                other_layer.array[r, c] = np.nan

                    elif erase_type == EraseType.Hill:

                        sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                        o_fct = 1 - sq / span_sq
                        rnd_value = random.uniform(0, 1)
                        if rnd_value > o_fct:
                            self.array[r, c] = np.nan
                            for other_layer in other_layers:
                                other_layer.array[r, c] = np.nan

                    else:
                        raise RuntimeError("unknown erase type: %s" % erase_type)

                if self.is_vector():
                    feature = self.feature_at_row_col(r=r, c=c)
                    if feature is not None:
                        feature['flagged'] = True

        self._modified_after_last_save = True
        self.plot.updated_layer_array()

    def modify(self, pnt_x, pnt_y, sz: int = 0, use_radius: bool = False, whole: bool = False,
               filter_type=FilterType.Gaussian, random_noise: bool = False) -> None:
        logger.debug("modify -> (%d, %d), size: %d, use radius: %s, random noise: %s"
                     % (pnt_x, pnt_y, sz, use_radius, random_noise))

        pnt_c, pnt_r = self.xy2cr(x=pnt_x, y=pnt_y)
        if (pnt_c is None) or (pnt_r is None):
            return

        self.store_undo_array()

        span = sz - 1
        span_sq = span * span

        if filter_type in [FilterType.Gaussian, FilterType.Median]:

            if whole:
                self._modify_whole(filter_type=filter_type,
                                   random_noise=random_noise)
            else:
                self._modify_point(pnt_r=pnt_r, pnt_c=pnt_c, filter_type=filter_type,
                                   span=span, span_sq=span_sq, use_radius=use_radius,
                                   random_noise=random_noise)

        else:
            raise RuntimeError("unknown filter: %s" % filter_type)

        self._modified_after_last_save = True
        self.plot.updated_layer_array()

    def _modify_whole(self, filter_type: FilterType, random_noise: bool) -> None:
        logger.debug("filter to whole bathy raster")

        loc_array = self.array[:]
        # logger.debug("loc array:\n%s" % loc_array)

        if filter_type == FilterType.Gaussian:
            # A filter which ignores NaNs is obtained by:
            # - Applying a standard filter to two auxiliary arrays V and W, and
            # - Taking the ratio of the two.
            v = loc_array.copy()
            v[np.isnan(loc_array)] = 0
            vv = ndimage.gaussian_filter(v, sigma=4.0)
            w = 0 * loc_array.copy() + 1
            w[np.isnan(loc_array)] = 0
            ww = ndimage.gaussian_filter(w, sigma=4.0)
            loc_array = vv / ww
        elif filter_type == FilterType.Median:
            v = loc_array.copy()
            loc_array = ndimage.median_filter(v, footprint=3)
        else:
            raise RuntimeError("unknown filter: %s" % filter_type)

        # logger.debug("smoothed array:\n%s" % loc_array)
        self.array = loc_array[:]

        if random_noise:
            logger.warning("not implemented")

    def _modify_point(self, pnt_r, pnt_c, filter_type: FilterType,
                      span: int, span_sq: int, use_radius: bool, random_noise: bool) -> None:
        logger.debug("filter to picked point")

        # create and populate the array to apply the filter to
        dim = 1 + span * 2
        loc_array = np.ndarray((dim, dim), dtype=np.float32)
        loc_array[:] = np.nan  # initialize to nan
        for dc in range(-span, span + 1):
            for dr in range(-span, span + 1):
                if use_radius:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    if sq > span_sq:
                        continue
                r = pnt_r + dr
                c = pnt_c + dc
                if (r < 0) or (r >= self.array.shape[0]):
                    continue
                elif (c < 0) or (c >= self.array.shape[1]):
                    continue
                loc_array[span + dr, span + dc] = self.array[r, c]

        # logger.debug("loc array:\n%s" % loc_array)

        def compare_nan_array(func, a, thresh):
            out = ~np.isnan(a)
            out[out] = func(a[out], thresh)
            return out

        loc_median = np.nanmedian(loc_array)
        loc_std = np.nanstd(loc_array)
        loc_delta = np.abs(loc_array - loc_median)
        flags = compare_nan_array(np.greater, loc_delta, 1.5 * loc_std)
        loc_array[flags] = np.nan
        # logger.debug("medianed array:\n%s" % loc_array)

        if filter_type == FilterType.Gaussian:
            # A Gaussian filter which ignores NaNs is obtained by:
            # - Applying a standard Gaussian filter to two auxiliary arrays V and W, and
            # - Taking the ratio of the two.
            v = loc_array.copy()
            v[np.isnan(loc_array)] = 0
            vv = ndimage.gaussian_filter(v, sigma=3.0)
            w = 0 * loc_array.copy() + 1
            w[np.isnan(loc_array)] = 0
            ww = ndimage.gaussian_filter(w, sigma=3.0)
            loc_array = vv / ww
        elif filter_type == FilterType.Median:
            v = loc_array.copy()
            # noinspection PyBroadException
            try:
                loc_array = ndimage.generic_filter(v, np.nanmedian, size=span - 2)
            except Exception:
                loc_array = ndimage.generic_filter(v, np.nanmedian, size=span)
        else:
            raise RuntimeError("unknown filter: %s" % filter_type)

        # logger.debug("smoothed array:\n%s" % loc_array)

        for dc in range(-span, span + 1):
            for dr in range(-span, span + 1):
                if use_radius:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    if sq > span_sq:
                        continue
                r = pnt_r + dr
                c = pnt_c + dc
                if (r < 0) or (r >= self.array.shape[0]):
                    continue
                elif (c < 0) or (c >= self.array.shape[1]):
                    continue

                self.array[r, c] = loc_array[span + dr, span + dc]
                if random_noise:
                    self.array[r, c] += ((np.random.random_sample() * 1.6 - 0.8) * loc_std)

    def clone(self, pnt_x, pnt_y, clone_x, clone_y, sz: int = 0, use_radius: bool = False,
              filter_type: CloneType = CloneType.Plain) -> None:
        logger.debug("clone -> (%d, %d)>>(%d, %d), size: %d, use radius: %s, filter: %s"
                     % (clone_x, clone_y, pnt_x, pnt_y, sz, use_radius, filter_type))

        pnt_c, pnt_r = self.xy2cr(x=pnt_x, y=pnt_y)
        if (pnt_c is None) or (pnt_r is None):
            return

        clone_c, clone_r = self.xy2cr(x=clone_x, y=clone_y)
        if (pnt_c is None) or (pnt_r is None):
            return

        self.store_undo_array()

        span = sz - 1
        span_sq = span * span

        # this filter require the calculation of the average value for the clone area
        i_sum = 0.0
        i_valid = 0
        i_avg = 0.0
        if filter_type in [CloneType.Noise, CloneType.BellNoise, CloneType.TriangleNoise]:
            for dc in range(-span, span + 1):

                for dr in range(-span, span + 1):

                    if use_radius:
                        sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                        if sq > span_sq:
                            continue

                    i_r = clone_r + dr
                    i_c = clone_c + dc

                    if (i_r < 0) or (i_r >= self.array.shape[0]):
                        continue
                    elif (i_c < 0) or (i_c >= self.array.shape[1]):
                        continue

                    if np.isnan(self.array[i_r, i_c]):
                        continue

                    i_valid += 1
                    i_sum += self.array[i_r, i_c]
        if i_valid > 0:
            i_avg = i_sum / i_valid

        for dc in range(-span, span + 1):

            for dr in range(-span, span + 1):

                if use_radius:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    if sq > span_sq:
                        continue

                i_r = clone_r + dr
                i_c = clone_c + dc

                if (i_r < 0) or (i_r >= self.array.shape[0]):
                    continue
                elif (i_c < 0) or (i_c >= self.array.shape[1]):
                    continue

                o_r = pnt_r + dr
                o_c = pnt_c + dc

                if (o_r < 0) or (o_r >= self.array.shape[0]):
                    continue
                elif (o_c < 0) or (o_c >= self.array.shape[1]):
                    continue

                if filter_type == CloneType.Bell:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    o_fct = sq / span_sq
                    i_fct = 1. - o_fct
                    self.array[o_r, o_c] = self.array[i_r, i_c] * i_fct + self.array[o_r, o_c] * o_fct

                elif filter_type == CloneType.Hill:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    i_fct = sq / span_sq
                    o_fct = 1. - i_fct
                    self.array[o_r, o_c] = self.array[i_r, i_c] * i_fct + self.array[o_r, o_c] * o_fct

                elif filter_type == CloneType.Triangle:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    dist = math.sqrt(sq)
                    o_fct = dist / span
                    i_fct = 1. - o_fct
                    self.array[o_r, o_c] = self.array[i_r, i_c] * i_fct + self.array[o_r, o_c] * o_fct

                elif filter_type == CloneType.Averaged:
                    self.array[o_r, o_c] = (self.array[i_r, i_c] + self.array[o_r, o_c]) / 2.0

                elif filter_type == CloneType.Noise:
                    self.array[o_r, o_c] += self.array[i_r, i_c] - i_avg

                elif filter_type == CloneType.BellNoise:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    o_fct = sq / span_sq
                    i_fct = 1. - o_fct
                    self.array[o_r, o_c] += (self.array[i_r, i_c] - i_avg) * i_fct

                elif filter_type == CloneType.TriangleNoise:
                    sq = abs(dc) * abs(dc) + abs(dr) * abs(dr)
                    dist = math.sqrt(sq)
                    o_fct = dist / span
                    i_fct = 1. - o_fct
                    self.array[o_r, o_c] += (self.array[i_r, i_c] - i_avg) * i_fct

                else:
                    self.array[o_r, o_c] = self.array[i_r, i_c]

        self._modified_after_last_save = True
        self.plot.updated_layer_array()

    # ### OTHER ###

    def info_str(self):

        msg = "- layer type: %s\n" % self._layer_type
        msg += "- format type: %s\n" % self._format_type

        if self.is_raster():
            if self._array is None:
                msg += "- array: %s\n" % self._array
            else:
                msg += "- array: %s [%s]\n" % (self._array.shape, self._array.dtype)

        if self.is_vector():
            msg += "- features: %d\n" % len(self._features)

        msg += "%s" % self.meta.str_info()

        msg += "- modified (after last save): %s\n" % self.modified
        msg += "- undo array available: %d\n" % self.number_of_undo_array_available()
        msg += "- undo features available: %d\n" % self.number_of_undo_features_available()

        return msg

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <layer type: %s>\n" % self._layer_type
        msg += "  <format type: %s>\n" % self._format_type

        if self.is_raster():
            if self._array is None:
                msg += "  <array: %s>\n" % self._array
            else:
                msg += "  <array: %s [%s]>\n" % (self._array.shape, self._array.dtype)

        if self.is_vector():
            msg += "  <features: %d>\n" % len(self._features)

        msg += "  %s" % self.meta

        msg += "  <modified (after last save): %s>\n" % self.modified

        msg += "  <undo array available: %d>\n" % self.number_of_undo_array_available()
        msg += "  <undo features available: %d>\n" % self.number_of_undo_features_available()

        return msg
