import matplotlib.pyplot as plt
from enum import Enum

class GeoRef(Enum):
    Geographic = 0
    UTM = 1


class Plots:

    def __init__(self):
        self.params = self.Params()

    def plot_ping_beam(self, data, colormap=None, title=None, xlabel=None, ylabel=None, clabel=None):  # TODO: Implement **kwargs
        if colormap is None:
            colormap = self.params.cmap
        if title is None:
            title = self.params.title
        if xlabel is None:
            xlabel = "Beam [#]"
        if ylabel is None:
            ylabel = "Ping [#]"
        if clabel is None:
            clabel = "Intensity [dB re Arbitrary]"

        fig_ping_beam = plt.figure()
        plt.imshow(data, cmap=colormap)
        cbar = plt.colorbar()
        cbar.set_label(clabel)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)

        return fig_ping_beam

    def plot_geo_ref(self, data, title=None, cmap=None, ref_freame=GeoRef.UTM):
        if title is None:
            title = self.params.title
        if cmap is None:
            cmap = self.params.cmap

        if ref_freame == GeoRef.UTM:
            self.params.xlabel = 'Eastings [m]'
            self.params.ylabel = 'Northings [m]'
        elif ref_freame == GeoRef.Geographic:
            self.params.xlabel = 'Longitude'
            self.params.ylabel = 'Latitude'

        fig_geo_ref = plt.figure()

    class Params:

        def __init__(self):
            self.linewidth = 2
            self.cmap = 'Greys_r'
            self.grid = True
            self.xlabel = "INSERT X LABEL"
            self.ylabel = "INSERT Y LABEL"
            self.title = "INSERT TITLE"
            self.cbar_label = "LABEL COLORBAR"
