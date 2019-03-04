from typing import Optional, TYPE_CHECKING

import numpy as np
from matplotlib.colors import Colormap

from hyo2.openbst.lib.plotting import Plotting
from hyo2.openbst.lib.sources.layer_type import LayerType

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from hyo2.openbst.lib.sources.layer import Layer


class LayerPlot:
    default_with_shading: bool = False
    default_shade_exag: float = 1.0
    default_shade_az: float = 315.0
    default_shade_elev: float = 45.0

    def __init__(self, layer: 'Layer'):
        self._layer = layer

        self._xs = None
        self._ys = None

        self._array_min = None
        self._array_max = None

        self._shaded = None
        self._with_shading = self.default_with_shading
        self._shade_exag = self.default_shade_exag
        self._shade_az = self.default_shade_az
        self._shade_elev = self.default_shade_elev

        self._cmap = None
        self.init_cmap()

    def validate_rect_slice(self, slc) -> tuple:
        slc0_start = slc[0].start
        slc0_end = slc[0].stop
        slc1_start = slc[1].start
        slc1_end = slc[1].stop

        if slc0_start < 0:
            slc0_start = 0

        if slc0_end > self._layer.array.shape[0]:
            slc0_end = self._layer.array.shape[0]

        if slc1_start < 0:
            slc1_start = 0

        if slc1_end > self._layer.array.shape[1]:
            slc1_end = self._layer.array.shape[1]

        return np.s_[slc0_start:slc0_end, slc1_start:slc1_end]

    def updated_layer_array(self, rect_slice: tuple = None) -> None:

        if rect_slice is None:
            rect_slice = np.s_[:, :]
        else:
            rect_slice = self.validate_rect_slice(slc=rect_slice)

        self._array_min = None
        self._array_max = None

        if self.with_shading:
            self.apply_shading(rect_slice=rect_slice, validate_slice=False)

    # ### EXTENT ###

    @property
    def xs(self) -> list:
        if self._xs is None:
            self.calc_xs()
        return self._xs

    def calc_xs(self) -> None:
        if self._layer.array is None:
            self._xs = list()
            return

        if not self._layer.meta.has_spatial_info:
            self._xs = [x for x in range(self._layer.array.shape[1])]
            return

        self._xs = \
            [(self._layer.meta.x_min + x * self._layer.meta.x_res)
             for x in range(self._layer.array.shape[1] + 1)]

    @property
    def ys(self) -> list:
        if self._ys is None:
            self.calc_ys()
        return self._ys

    def calc_ys(self) -> None:
        if self._layer.array is None:
            self._ys = list()
            return

        if not self._layer.meta.has_spatial_info:
            self._ys = [y for y in range(self._layer.array.shape[0])]
            return

        self._ys = \
            [(self._layer.meta.y_min + y * self._layer.meta.y_res)
             for y in range(self._layer.array.shape[0] + 1)]

    @property
    def extent(self) -> tuple:
        return self.xs[0], self.xs[-1], self.ys[0], self.ys[-1]

    # ### COLORMAP ###

    def init_cmap(self):
        if self._layer.layer_type == LayerType.BATHYMETRY:
            self._cmap = Plotting.bathy_cmap

        elif self._layer.layer_type == LayerType.UNCERTAINTY:
            self._cmap = Plotting.uncertainty_cmap

        elif self._layer.layer_type == LayerType.MOSAIC:
            self._cmap = Plotting.mosaic_cmap

        else:
            self._cmap = Plotting.default_cmap

    @property
    def cmap(self) -> Colormap:
        return self._cmap

    @cmap.setter
    def cmap(self, value: Colormap) -> None:
        self._cmap = value

    @property
    def array_min(self) -> float:
        if self._array_min is None:
            self._array_min = self._layer.array_min
        return self._array_min

    @array_min.setter
    def array_min(self, value: float) -> None:
        self._array_min = value

    @property
    def array_max(self) -> float:
        if self._array_max is None:
            self._array_max = self._layer.array_max
        return self._array_max

    @array_max.setter
    def array_max(self, value: float) -> None:
        self._array_max = value

    @property
    def clim(self) -> tuple:
        return self.array_min, self.array_max

    # ### SHADING ###

    def is_shadable(self) -> bool:
        return self._layer.layer_type == LayerType.BATHYMETRY

    @property
    def shade_exag(self) -> float:
        return self._shade_exag

    @shade_exag.setter
    def shade_exag(self, value: float) -> None:
        self._shade_exag = value

    @property
    def shade_az(self) -> float:
        return self._shade_az

    @shade_az.setter
    def shade_az(self, value: float) -> None:
        self._shade_az = value

    @property
    def shade_elev(self) -> float:
        return self._shade_elev

    @shade_elev.setter
    def shade_elev(self, value: float) -> None:
        self._shade_elev = value

    @property
    def shaded(self) -> Optional[np.ndarray]:
        return self._shaded

    @property
    def with_shading(self) -> bool:
        return self._with_shading

    @with_shading.setter
    def with_shading(self, value: bool) -> None:
        self._with_shading = value

    def apply_shading(self, rect_slice: tuple = None, validate_slice: bool = True) -> None:

        if not self.with_shading:
            return

        if self._layer.array is None:
            raise RuntimeError("Attempting to shading None array")

        if rect_slice is None:
            rect_slice = np.s_[:, :]
        else:
            if validate_slice:
                rect_slice = self.validate_rect_slice(slc=rect_slice)

        if self._shaded is None:
            self._shaded = np.empty_like(self._layer.array)
            self._shaded[:] = np.nan

        x, y = np.gradient(self._layer.array[rect_slice] * self._shade_exag)
        slope = np.pi / 2. - np.arctan(np.sqrt(x * x + y * y))
        aspect = np.arctan2(-x, y)
        az_rad = self._shade_az * np.pi / 180.
        elev_rad = self._shade_elev * np.pi / 180.

        rect_shaded = np.sin(elev_rad) * np.sin(slope) + np.cos(elev_rad) * np.cos(slope) * np.cos(
            az_rad - aspect)

        self._shaded[rect_slice] = (rect_shaded + 1) / 2

    def reset_shading_settings(self):
        self._with_shading = self.default_with_shading
        self._shade_exag = self.default_shade_exag
        self._shade_az = self.default_shade_az
        self._shade_elev = self.default_shade_elev
