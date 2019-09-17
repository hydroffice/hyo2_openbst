import matplotlib.pyplot as plt
from enum import Enum


class GeoRef(Enum):
    Geographic = 0
    UTM = 1


class Plots:

    def __init__(self):
        self.params = self.Params()

    def plot_ping_beam(self, data, title=None, cmap=None): # TODO: Implement **kwargs
        if title is None:
            title = self.params.title
        if cmap is None:
            cmap = self.params.cmap

        self.params.xlabel = "Beam [#]"
        self.params.ylabel = "Ping [#]"

        fig_ping_beam = plt.figure()
        plt.imshow(data, cmap=self.params.cmap)
        cbar = plt.colorbar()
        cbar.set_label(self.params.cbar_label)
        plt.xlabel(self.params.xlabel)
        plt.ylabel(self.params.ylabel)
        plt.title(self.params.title)

        return fig_ping_beam

    def plot_geo_ref(self, data, title=None, cmap=None, ref_freame=GeoRef.UTM):
        if title is None:
            title = self.params.title
        if cmap is None:
            cmap = self.params.cmap

        if ref_freame == GeoRef.UTM:
            self.params.xlabel =

    class Params:

        def __init__(self):
            self.linewidth = 2
            self.cmap = 'Greys_r'
            self.grid = True
            self.xlabel = "INSERT X LABEL"
            self.ylabel = "INSERT Y LABEL"
            self.title = "INSERT TITLE"
            self.cbar_label = "LABEL COLORBAR"
