import logging
import os

from PySide2 import QtGui
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends import qt_compat
from hyo2.openbst.app import app_info

logger = logging.getLogger(__name__)


class NavToolbar(NavigationToolbar2QT):

    def __init__(self, canvas, parent):
        NavigationToolbar2QT.__init__(self, canvas=canvas, parent=parent)

    def _icon(self, name):
        if qt_compat.is_pyqt5():
            name = name.replace('.png', '_large.png')
        # TODO
        # ### TO BE MODIFIED ###
        icon_path = os.path.join(app_info.app_media_path, name)
        # logger.debug("nav toolbar icon: %s" % icon_path)
        pm = QtGui.QPixmap(icon_path)
        # ################

        if hasattr(pm, 'setDevicePixelRatio'):
            pm.setDevicePixelRatio(self.canvas._dpi_ratio)
        return QtGui.QIcon(pm)
