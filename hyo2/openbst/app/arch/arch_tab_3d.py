import logging
from typing import Optional
import numpy as np

from PySide2 import QtCore, QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc_context
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import LightSource

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.openbst.app.arch import app_info
from hyo2.openbst.app.arch.navigation_toolbar import NavToolbar
from hyo2.openbst.lib.models.jackson2.model import Model
from hyo2.openbst.lib.models.jackson2.dicts import test_params, TestSediments
from hyo2.openbst.lib.models.jackson2.plot_params import PlotParams

matplotlib.use('Qt5Agg')
matplotlib.rcParams['axes.formatter.useoffset'] = False

logger = logging.getLogger(__name__)


class ArchTab3D(QtWidgets.QMainWindow):
    color_tot = '#57a3e5'
    color_rough = '#1f8e44'
    color_vol = '#8c0c54'
    color_loss = '#f99a25'
    color_grid = '#cccccc'
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

        self.setWindowTitle("Arch Tab 3D")
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
            self.up_ax = self.f.add_subplot(111, projection='3d')

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

        self._last_sed = str()
        self._ss = None
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

        self.jm2.mdl_params.f = self.freq_slider.value() * 1000
        self.jm2.sed_params = test_params[self.seds[cur_sed]]
        self.jm2.run()

        self.freq_label.setText("Frequency [%.1f kHz]" % (self.jm2.mdl_params.f / 1000))

        self.up_ax.clear()

        freqs = [1.0, 3.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0, 75.0, 100.0, 150.0, 200.0, 300.0, 500.0]
        thetas = self.jm2.out.theta_i
        x, y = np.meshgrid(thetas, freqs)
        if self._last_sed != cur_sed:
            logger.debug("recalculating thetas, freqs, and ss ...")

            self._ss = np.full((len(freqs), thetas.size), np.nan)

            for i, f in enumerate(freqs):
                jm2 = Model()
                jm2.use_default_mdl_params()
                jm2.mdl_params.f = f
                jm2.use_test_sed_params(self.seds[cur_sed])
                jm2.run()

                for j, theta in enumerate(range(jm2.out.theta_i.size)):
                    self._ss[i, j] = jm2.out.ss_tot[j]

            self._last_sed = cur_sed
            logger.debug("recalculating thetas, freqs, and ss: DONE")

        with rc_context(app_info.plot_rc_context):
            self.f.suptitle("APL-UW Elastic Scattering Model v.2017 - %s - %.1f kHz"
                            % (self.jm2.sed_params.name, (self.jm2.mdl_params.f / 1000)))

            if self._ss is not None:
                # ls = LightSource(270, 45)
                # rgb = ls.shade(ss, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
                self.up_ax.plot_surface(x, y, self._ss, rstride=1, cstride=1, alpha=0.8,
                                        cmap='Greys', edgecolor='none',
                                        # shade=False, facecolors=rgb
                                        )

            freqs = np.full_like(self.jm2.out.ss_tot, self.freq_slider.value())
            self.up_ax.plot(self.jm2.out.theta_i, freqs, self.jm2.out.ss_tot, color=self.color_tot, linestyle='-',
                            label="Total SS")
            self.up_ax.set_xlim(0.0, 90.0)
            self.up_ax.set_ylim(1.0, 500.0)
            self.up_ax.set_zlim(self._pp.db_min, self._pp.db_max)
            # self.up_ax.grid(color=self.color_grid)
            self.up_ax.set_xlabel('Incidence Angle [deg]')
            self.up_ax.set_ylabel('Frequency [kHz]')
            self.up_ax.set_zlabel('Scattering Strength [dB]')

            self.c.draw()

    # ### ICON SIZE ###

    def toolbars_icon_size(self) -> int:
        return self.file_products_bar.iconSize().height()

    def set_toolbars_icon_size(self, icon_size: int) -> None:
        # self.file_products_bar.setIconSize(QtCore.QSize(icon_size, icon_size))
        pass
