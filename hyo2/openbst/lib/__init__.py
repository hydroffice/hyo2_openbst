import os
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.openbst import name
from hyo2.openbst import __version__


lib_info = LibInfo()

lib_info.lib_name = name
lib_info.lib_version = __version__
lib_info.lib_author = "G.Masetti (CCOM/JHC); Jean-Marie Augustin (IFREMER); Cyrille Poncelet (IFREMER)"
lib_info.lib_author_email = "gmasetti@ccom.unh.edu; jean.marie.augustin@ifremer.fr; cyrille.poncelet@ifremer.fr"

lib_info.lib_license = "LGPL v3"
lib_info.lib_license_url = "https://www.hydroffice.org/license/"

lib_info.lib_path = os.path.abspath(os.path.dirname(__file__))

lib_info.lib_url = "https://www.hydroffice.org/openbst/"
lib_info.lib_manual_url = "https://www.hydroffice.org/manuals/openbst/index.html"
lib_info.lib_support_email = "openbst@hydroffice.org"
lib_info.lib_latest_url = "https://www.hydroffice.org/latest/openbst.txt"

lib_info.lib_dep_dict = {
    "hyo2.abc": "hyo2.abc",
    "gdal": "osgeo",
    "numpy": "numpy",
    "scipy": "scipy",
    "pyproj": "pyproj",
    "h5py": "h5py",
    "netCDF4": "netCDF4",
    "PySide2": "PySide2",
    "matplotlib": "matplotlib"
}
