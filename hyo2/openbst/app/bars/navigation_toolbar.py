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

    def release_zoom(self, event):
        """Callback for mouse button release in zoom to rect mode."""
        for zoom_id in self._ids_zoom:
            self.canvas.mpl_disconnect(zoom_id)
        self._ids_zoom = []

        self.remove_rubberband()

        if not self._xypress:
            return

        last_a = []

        for cur_xypress in self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, ind, view = cur_xypress
            # ignore singular clicks - 5 pixels is a threshold
            # allows the user to "cancel" a zoom action
            # by zooming by less than 5 pixels
            if ((abs(x - lastx) < 5 and self._zoom_mode != "y") or
                    (abs(y - lasty) < 5 and self._zoom_mode != "x")):
                self._xypress = None
                self.release(event)
                self.draw()
                return

            # detect twinx,y axes and avoid double zooming
            twinx, twiny = False, False
            if last_a:
                for la in last_a:
                    if a.get_shared_x_axes().joined(a, la):
                        twinx = True
                    if a.get_shared_y_axes().joined(a, la):
                        twiny = True
            last_a.append(a)

            if self._button_pressed == 1:
                direction = 'in'
            elif self._button_pressed == 3:
                direction = 'out'
            else:
                continue

            # ### ADDED ###
            # try to keep the original ratio
            # - get the axis limits
            x_min, x_max = a.get_xlim()
            y_min, y_max = a.get_ylim()
            # - get the limits of the axes
            d2c = a.transData.transform
            ax_x_min, ax_y_min = d2c((x_min, y_min))
            ax_x_max, ax_y_max = d2c((x_max, y_max))
            ax_width = abs(ax_x_max - ax_x_min)
            ax_height = ax_y_max - ax_y_min
            # - calculate axis ratio
            ax_ratio = ax_width / ax_height
            # logger.debug("axes ratio: %s" % (ax_ratio, ))
            bb_width = abs(lastx - x)
            bb_height = abs(lasty - y)
            # - calculate bbox ratio
            bb_ratio = bb_width / bb_height
            # logger.debug("bbox ratio: %s" % (bb_ratio, ))
            # - use the ratio of the ratios to calculate the delta x
            ratio = ax_ratio / bb_ratio
            delta = (bb_width * ratio - bb_width) / 2.0
            # ############
            # # MODIFIED #
            # - apply the delta x on both sides
            # noinspection PyProtectedMember
            a._set_view_from_bbox((lastx - delta, lasty, x + delta, y), direction, self._zoom_mode, twinx, twiny)
            # ############

        self.draw()
        self._xypress = None
        self._button_pressed = None

        self._zoom_mode = None

        self.push_current()
        self.release(event)

        # ### ADDED ###
        # Modified the behavior to deselect 'Zoom' after each action
        super(NavigationToolbar2QT, self).zoom()
        self._update_buttons_checked()
        # #############
