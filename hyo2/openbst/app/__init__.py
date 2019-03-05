import os
from hyo2.openbst.lib.plotting import Plotting  # on Linux, this must be imported first
from hyo2.abc.app.app_info import AppInfo
from hyo2.openbst import name
from hyo2.openbst import __version__


app_info = AppInfo()

app_info.app_name = name
app_info.app_version = __version__
app_info.app_author = "G.Masetti (CCOM/JHC); Jean-Marie Augustin (IFREMER); Cyrille Poncelet (IFREMER)"
app_info.app_author_email = "gmasetti@ccom.unh.edu; jean.marie.augustin@ifremer.fr; cyrille.poncelet@ifremer.fr"

app_info.app_license = "LGPL v3"
app_info.app_license_url = "https://www.hydroffice.org/license/"

app_info.app_path = os.path.abspath(os.path.dirname(__file__))

app_info.app_url = "https://www.hydroffice.org/openbst/"
app_info.app_manual_url = "https://www.hydroffice.org/manuals/openbst/index.html"
app_info.app_support_email = "openbst@hydroffice.org"
app_info.app_latest_url = "https://www.hydroffice.org/latest/openbst.txt"

app_info.app_media_path = os.path.join(app_info.app_path, "media")
app_info.app_main_window_object_name = "MainWindow"
app_info.app_license_path = os.path.join(app_info.app_media_path, "LICENSE")
app_info.app_icon_path = os.path.join(app_info.app_media_path, "app_icon.png")

# icon size
app_info.app_tabs_icon_size = 36
app_info.app_toolbars_icon_size = 24

# APPENDED to the AppInfo class

# button size
app_info.app_button_height = 24

app_info.plot_font_size = 9
app_info.plot_rc_context = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Tahoma', 'Bitstream Vera Sans', 'Lucida Grande', 'Verdana'],
        'font.size': app_info.plot_font_size,
        'figure.titlesize': app_info.plot_font_size + 1,
        'axes.labelsize': app_info.plot_font_size,
        'legend.fontsize': app_info.plot_font_size,
        'xtick.labelsize': app_info.plot_font_size - 1,
        'ytick.labelsize': app_info.plot_font_size - 1,
        'axes.linewidth': 0.5,
        'axes.xmargin': 0.01,
        'axes.ymargin': 0.01,
        'lines.linewidth': 1.0,
        'grid.alpha': 0.2,
    }

app_info.plot_bathy_cmap = Plotting.default_cmap
app_info.plot_imagery_cmap = Plotting.default_cmap

# settings

app_info.key_show_welcome_dialog = "show_welcome_dialog"
app_info.key_max_undo_steps = "max_undo_steps"
app_info.key_show_mouse_patch = "show_mouse_patch"
app_info.key_raster_import_folder = "raster_import_folder"
app_info.key_raster_export_folder = "raster_export_folder"
