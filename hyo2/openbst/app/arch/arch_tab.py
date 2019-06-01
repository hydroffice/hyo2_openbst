import logging
from typing import Optional

from PySide2 import QtCore, QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc_context
import matplotlib.gridspec as gridspec

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.openbst.app.arch import app_info
from hyo2.openbst.app.arch.navigation_toolbar import NavToolbar
from hyo2.openbst.lib.models.jackson2.model import Model
from hyo2.openbst.lib.models.jackson2.dicts import test_params, TestSediments
from hyo2.openbst.lib.models.jackson2.plot_params import PlotParams

matplotlib.use('Qt5Agg')
matplotlib.rcParams['axes.formatter.useoffset'] = False

logger = logging.getLogger(__name__)


class ArchTab(QtWidgets.QMainWindow):

    color_tot = '#57a3e5'
    color_rough = '#1f8e44'
    color_vol = '#8c0c54'
    color_loss = '#f99a25'
    color_grid = '#dddddd'
    color_comp = '#CC0000'

    def __init__(self, main_win, plot_params: Optional[PlotParams] = None):
        super().__init__(parent=main_win)
        if plot_params is None:
            self._pp = PlotParams()  # plot parameters
        else:
            self._pp = plot_params

        self.jm2 = Model()
        self.jm2.use_test_sed_params(TestSediments.COARSE_SAND)
        self.jm2.use_default_mdl_params()

        self.setWindowTitle("Arch Tab")
        self.settings = QtCore.QSettings()

        self.main_win = main_win
        self.progress = QtProgress(parent=self)

        self.setContentsMargins(0, 0, 0, 0)

        canvas_frame = QtWidgets.QFrame(self)
        self.layout = QtWidgets.QVBoxLayout()
        canvas_frame.setLayout(self.layout)

        with rc_context(app_info.plot_rc_context):

            self.f = Figure()
            self.f.patch.set_alpha(0.0)
            self.c = FigureCanvas(self.f)
            self.c.setParent(self)
            # noinspection PyUnresolvedReferences
            self.c.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c.setFocus()
            self.layout.addWidget(self.c)

            # axes
            gs = gridspec.GridSpec(3, 3)
            self.up_ax = self.f.add_subplot(gs[0:2, :])
            self.down_ax = self.f.add_subplot(gs[2, :])

        # navigation
        self.nav = NavToolbar(canvas=self.c, parent=self)
        self.layout.addWidget(self.nav)

        self.setCentralWidget(canvas_frame)

        settings_dock = QtWidgets.QDockWidget("Settings")
        settings_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable |
                                  QtWidgets.QDockWidget.DockWidgetMovable)
        settings_dock.setMinimumWidth(200)
        settings_dock.setMaximumWidth(400)
        settings_frame = QtWidgets.QWidget()
        settings_dock.setWidget(settings_frame)
        self.process_layout = QtWidgets.QVBoxLayout()
        settings_frame.setLayout(self.process_layout)
        
        # sediment

        seds_label_layout = QtWidgets.QHBoxLayout()
        self.process_layout.addLayout(seds_label_layout)
        seds_label_layout.addStretch()
        seds_label = QtWidgets.QLabel("Sediment Type")
        seds_label_layout.addWidget(seds_label)
        seds_label_layout.addStretch()

        seds_layout = QtWidgets.QHBoxLayout()
        self.process_layout.addLayout(seds_layout)
        seds_layout.addStretch()
        self.seds = dict()
        for sed in TestSediments:
            self.seds[test_params[sed].name] = sed
        self.seds_list = QtWidgets.QComboBox()
        self.seds_list.addItems(list(self.seds.keys()))
        self.seds_list.setCurrentText(test_params[TestSediments.COARSE_SAND].name)
        # noinspection PyUnresolvedReferences
        self.seds_list.currentTextChanged.connect(self.on_draw)
        seds_layout.addWidget(self.seds_list)
        seds_layout.addStretch()
        
        # frequency

        freq_label_layout = QtWidgets.QHBoxLayout()
        self.process_layout.addLayout(freq_label_layout)
        freq_label_layout.addStretch()
        self.freq_label = QtWidgets.QLabel("Frequency [%.1f kHz]" % (self.jm2.mdl_params.f / 1000))
        freq_label_layout.addWidget(self.freq_label)
        freq_label_layout.addStretch()
        
        freq_layout = QtWidgets.QHBoxLayout()
        self.process_layout.addLayout(freq_layout)
        freq_layout.addStretch()
        self.freq_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.freq_slider.setMinimumWidth(160)
        self.freq_slider.setMinimum(1)
        self.freq_slider.setMaximum(500)
        self.freq_slider.setTickInterval(1)
        self.freq_slider.setValue(self.jm2.mdl_params.f / 1000)
        # noinspection PyUnresolvedReferences
        self.freq_slider.valueChanged.connect(self.on_draw)
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addStretch()

        self.process_layout.addSpacing(12)

        redraw_layout = QtWidgets.QHBoxLayout()
        self.process_layout.addLayout(redraw_layout)
        redraw_layout.addStretch()
        redraw_btn = QtWidgets.QPushButton("Redraw")
        # noinspection PyUnresolvedReferences
        redraw_btn.clicked.connect(self.on_draw)
        redraw_layout.addWidget(redraw_btn)
        redraw_layout.addStretch()

        self.process_layout.addStretch()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, settings_dock)

        self.on_draw()

    @property
    def plt_params(self):
        return self._pp

    @plt_params.setter
    def plt_params(self, params):
        if not isinstance(params, PlotParams):
            raise Exception("invalid type for passed Plot Parameters: %s" % type(params))
        self._pp = params

    def on_draw(self):
        logger.debug("redraw")

        cur_sed = self.seds_list.currentText()
        cur_freq_khz = self.freq_slider.value()

        self.jm2.mdl_params.f = cur_freq_khz * 1000
        self.jm2.use_test_sed_params(self.seds[cur_sed])
        self.jm2.run()

        self.freq_label.setText("Frequency [%.1f kHz]" % (cur_freq_khz, ))

        self.up_ax.clear()
        self.down_ax.clear()

        with rc_context(app_info.plot_rc_context):

            self.f.suptitle("APL-UW Elastic Scattering Model v.2017 - %s - %.1f kHz"
                            % (cur_sed, cur_freq_khz))

            self.up_ax.plot(self.jm2.out.theta_i, self.jm2.out.ss_tot, color=self.color_tot, linestyle='-',
                            label="Total SS")
            self.up_ax.plot(self.jm2.out.theta_i, self.jm2.out.ss_rough, color=self.color_rough, linestyle='--',
                            label="Roughness-only SS")
            self.up_ax.plot(self.jm2.out.theta_i, self.jm2.out.ss_vol, color=self.color_vol, linestyle=':',
                            label="Volume-only SS")
            self.up_ax.set_xlim(0.0, 90.0)
            self.up_ax.set_ylim(self._pp.db_min, self._pp.db_max)
            self.up_ax.legend()
            self.up_ax.grid(color=self.color_grid)
            # self.up_ax.set_xticklabels([])
            # self.up_ax.set_xlabel('Incidence Angle [deg]')
            self.up_ax.set_ylabel('Scattering Strength [dB]')

            self.down_ax.plot(self.jm2.out.theta_i, self.jm2.out.ref_loss, color=self.color_loss, linestyle='-',
                              label="Model")
            self.down_ax.set_xlim(0.0, 90.0)
            self.down_ax.set_ylim(0.0, 50.0)
            # self.down_ax.legend()
            self.down_ax.grid(color=self.color_grid)
            self.down_ax.set_xlabel('Incidence Angle [deg]')
            self.down_ax.set_ylabel('Reflection Loss [dB]')

            self.c.draw()

    def redraw(self):
        """Redraw the canvases, update the locators"""

        with rc_context(app_info.plot_rc_context):
            for a in self.c.figure.get_axes():

                xaxis = getattr(a, 'xaxis', None)
                yaxis = getattr(a, 'yaxis', None)
                locators = []

                if xaxis is not None:
                    locators.append(xaxis.get_major_locator())
                    locators.append(xaxis.get_minor_locator())

                if yaxis is not None:
                    locators.append(yaxis.get_major_locator())
                    locators.append(yaxis.get_minor_locator())

                for loc in locators:
                    loc.refresh()

            self.c.draw_idle()

    # ### ICON SIZE ###

    def toolbars_icon_size(self) -> int:
        return self.file_products_bar.iconSize().height()

    def set_toolbars_icon_size(self, icon_size: int) -> None:
        # self.file_products_bar.setIconSize(QtCore.QSize(icon_size, icon_size))
        pass
