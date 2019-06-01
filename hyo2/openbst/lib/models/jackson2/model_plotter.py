from typing import Optional

# noinspection PyUnresolvedReferences
from PySide2 import QtWidgets
from matplotlib import rc_context
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import logging

from hyo2.openbst.lib.models.jackson2.model import Model
from hyo2.openbst.lib.models.jackson2.model_output import ModelOutput
from hyo2.openbst.lib.models.jackson2.plot_params import PlotParams

logger = logging.getLogger(__name__)


class ModelPlotter:
    font_size = 7
    rc_context = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Tahoma', 'Bitstream Vera Sans', 'Lucida Grande', 'Verdana'],
        'font.size': font_size,
        'figure.titlesize': font_size + 1,
        'figure.figsize': (8, 6),
        'axes.labelsize': font_size,
        'legend.fontsize': font_size,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'axes.linewidth': 0.8,
        'axes.xmargin': 0.01,
        'axes.ymargin': 0.01,
        'lines.linewidth': 1.3,
    }
    color_tot = '#57a3e5'
    color_rough = '#1f8e44'
    color_vol = '#8c0c54'
    color_loss = '#f99a25'
    color_grid = '#cccccc'
    color_comp = '#CC0000'

    def __init__(self, mdl: Model, plot_params: Optional[PlotParams] = None):
        self._mdl = mdl  # model
        if plot_params is None:
            self._pp = PlotParams()  # plot parameters
        else:
            self._pp = plot_params

    @property
    def plt_params(self):
        return self._pp

    @plt_params.setter
    def plt_params(self, params):
        if not isinstance(params, PlotParams):
            raise Exception("invalid type for passed Plot Parameters: %s" % type(params))
        self._pp = params

    def plot(self, run_model: bool = True, out_compare: ModelOutput = ModelOutput()):
        if run_model:
            success = self._mdl.run()
            if not success:
                logger.warning("unable to run the model")
                return None

        with rc_context(self.rc_context):

            plt.ion()

            plt_name = "APL-UW Elastic Scattering Model v.2017 - %s" % self._mdl.sed_params.name
            plt.close(plt_name)
            plt.figure(plt_name)

            plt.suptitle(plt_name + " - %.1f kHz" % (self._mdl.mdl_params.f / 1000.0))

            gs = gridspec.GridSpec(3, 3)

            plt.subplot(gs[0:2, :])

            plt.plot(self._mdl.out.theta_g, self._mdl.out.ss_tot, color=self.color_tot, linestyle='-',
                     label="Model - Total SS")
            if (out_compare.theta_g is not None) and (out_compare.ss_tot is not None):
                plt.plot(out_compare.theta_g, out_compare.ss_tot, color=self.color_comp, linestyle='-',
                         label="Ref - Total SS")

            plt.plot(self._mdl.out.theta_g, self._mdl.out.ss_rough, color=self.color_rough, linestyle='--',
                     label="Model - Roughness-only SS")
            if (out_compare.theta_g is not None) and (out_compare.ss_rough is not None):
                plt.plot(out_compare.theta_g, out_compare.ss_rough, color=self.color_comp, linestyle='--',
                         label="Ref - Roughness-only SS")

            plt.plot(self._mdl.out.theta_g, self._mdl.out.ss_vol, color=self.color_vol, linestyle=':',
                     label="Ref - Volume-only SS")
            if (out_compare.theta_g is not None) and (out_compare.ss_vol is not None):
                plt.plot(out_compare.theta_g, out_compare.ss_vol, color=self.color_comp, linestyle=':',
                         label="Ref - Volume-only SS")

            plt.xlim(0.0, 90.0)
            plt.ylim(self._pp.db_min, self._pp.db_max)
            plt.legend()
            plt.grid(color=self.color_grid)
            # plt.xlabel('Grazing Angle [deg]')
            plt.ylabel('Scattering Strength [dB]')

            plt.subplot(gs[2, :])
            plt.plot(self._mdl.out.theta_g, self._mdl.out.ref_loss, color=self.color_loss, linestyle='-',
                     label="Model")
            if (out_compare.theta_g is not None) and (out_compare.ref_loss is not None):
                plt.plot(self._mdl.out.theta_g, self._mdl.out.ref_loss, color=self.color_comp, linestyle='-',
                         label="Reference")
            plt.xlim(0.0, 90.0)
            plt.ylim(0.0, 50.0)
            plt.xlabel('Grazing Angle [deg]')
            plt.ylabel('Reflection Loss [dB]')
            plt.grid(color=self.color_grid)

        return plt

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  %s" % self._mdl
        msg += "  %s" % self._pp

        return msg
