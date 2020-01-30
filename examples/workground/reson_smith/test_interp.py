import logging
from pathlib import Path

# from PySide2 import QtWidgets
# import matplotlib.pyplot as plt
# from netCDF4 import Dataset, Group, Variable
from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.process_methods.interpolation import InterpEnum

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# Set up project
testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
bst = OpenBST(prj_name="default", force_new=True).prj
# bst.open_project_folder()
raw_path = testing.download_data_folder().joinpath('reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()

# Test 1 - Method:Simplem, Pass = No Errors
bst.parameters.interpolation.method_type = InterpEnum.simple_linear
bst.interpolation()

# Inspect Data
# path_hash = bst.raws.raws_list[0]
# raw_file_path = bst.raws_folder.joinpath(path_hash + bst.raws.ext)
# process_file_path = bst.process_folder.joinpath(path_hash + bst.process.ext)
#
# ds_raw = Dataset(filename=raw_file_path, mode='r')
# ds_process = Dataset(filename=process_file_path, mode='r')
# grp_parent = ds_process.groups[bst.process.proc_manager.parent_process]
#
# # Grab raw data for comparison
# grp_position = ds_raw.groups['position']
#
# var_pos_time = grp_position.variables['time']
# var_latitude = grp_position.variables['latitude']
# var_longitude = grp_position.variables['longitude']
# data_pos_time = var_pos_time[:]
# data_latitude = var_latitude[:]
# data_longitude = var_longitude[:]
# 
# grp_attitude = ds_raw.groups['attitude']
#
# var_motion_time = grp_attitude.variables['time']
# var_pitch = grp_attitude.variables['pitch']
# var_roll = grp_attitude.variables['roll']
# var_heave = grp_attitude.variables['heave']
# var_heading_time = grp_attitude.variables['heading_time']
# var_heading = grp_attitude.variables['heading']
# data_motion_time = var_motion_time[:]
# data_pitch = var_pitch[:]
# data_roll = var_roll[:]
# data_heave = var_heave[:]
# data_heading_time = var_heading_time[:]
# data_heading = var_heading[:]

# # Grab process data
# var_time = grp_parent.variables['time']
# var_lat = grp_parent.variables['latitude']
# var_lon = grp_parent.variables['longitude']
# var_roll = grp_parent.variables['roll']
# var_pitch = grp_parent.variables['pitch']
# var_heave = grp_parent.variables['heave']
# var_heading = grp_parent.variables['yaw']
# time = var_time[:]
# lat_i = var_lat[:]
# lon_i = var_lon[:]
# roll_i = var_roll[:]
# pitch_i = var_pitch[:]
# yaw_i = var_heading[:]
# heave_i = var_heave[:]
#
# plt.figure()
# plt.plot(data_pos_time, data_latitude)
# plt.scatter(time, lat_i)
#
# plt.figure()
# plt.plot(data_pos_time, data_longitude)
# plt.scatter(time, lon_i)
#
# plt.figure()
# plt.plot(data_motion_time, data_pitch)
# plt.plot(data_motion_time, data_roll)
# plt.plot(data_motion_time, data_heave)
# plt.scatter(time, pitch_i)
# plt.scatter(time, roll_i)
# plt.scatter(time, heave_i)
#
# plt.figure()
# plt.plot(data_heading_time, data_heading)
# plt.scatter(time, yaw_i)
#
# plt.show()