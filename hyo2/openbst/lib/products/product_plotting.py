from matplotlib import colors, cm
from bidict import bidict
import numpy as np

import logging

logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
def make_shadow_cmap() -> colors.ListedColormap:
    shadow_colors = cm.Greys(np.arange(cm.Greys.N))
    mid_idx = int(cm.Greys.N * 0.8)
    shadow_colors[:mid_idx, 3] = 0.0  # avoid shadows at low values
    shadow_colors[mid_idx:, 3] = np.linspace(0.0, 1.0, num=(cm.Greys.N - mid_idx),
                                             endpoint=True)
    # logger.debug("shadow colors: %s" % shadow_colors[:, 3])

    return colors.ListedColormap(shadow_colors)


class ProductPlotting:

    default_cmap = cm.get_cmap("viridis")

    bathy_cmap = cm.get_cmap("gist_rainbow").reversed()

    ocean_cmap = colors.LinearSegmentedColormap.from_list("ocean",
                                                          ["#63006c", "#2b4ef4", "#2f73ff", "#4b8af4", "#bee2bf"],
                                                          gamma=0.5)
    cm.register_cmap(cmap=bathy_cmap)

    uncertainty_cmap = cm.get_cmap("RdYlGn")
    mosaic_cmap = cm.get_cmap("gray")

    magenta_color = '#bf00ff'
    orange_color = '#E69F24'
    blue_color = '#1C75C3'

    cmaps = bidict({
            "rainbow": cm.get_cmap("rainbow"),
            "gist_earth": cm.get_cmap("gist_earth"),
            "gist_ncar": cm.get_cmap("gist_ncar"),
            "gist_rainbow": cm.get_cmap("gist_rainbow"),
            "gist_rainbow_reversed": bathy_cmap,
            "terrain": cm.get_cmap("terrain"),
            "ocean": ocean_cmap,
            "RdYlGn": uncertainty_cmap,
            "gray": mosaic_cmap,
            "viridis": default_cmap,
            "RdYlBu_r": cm.get_cmap("RdYlBu_r"),
            "Oranges": cm.get_cmap("Oranges"),
            "Blues": cm.get_cmap("Blues"),
            "coolwarm": cm.get_cmap("coolwarm"),
            "RdBu": cm.get_cmap("RdBu"),
            "OrRd": cm.get_cmap("OrRd"),
            "cool": cm.get_cmap("cool"),
            "PuBu": cm.get_cmap("PuBu"),
            "hsv": cm.get_cmap("hsv"),
            "BuGn": cm.get_cmap("BuGn"),
            "RdPu": cm.get_cmap("RdPu"),
    })

    shadow_cmap = make_shadow_cmap()
