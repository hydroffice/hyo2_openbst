import logging
import numpy as np
# import traceback
from netCDF4 import Dataset
from pathlib import Path

from hyo2.openbst.lib import prr
from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST
from hyo2.openbst.lib.processing.process_methods.area_correction import AreaCorrectionEnum
from hyo2.openbst.lib.processing.process_methods.calibration import CalibrationEnum
from hyo2.openbst.lib.processing.process_methods.geolocate import Geolocation
from hyo2.openbst.lib.processing.process_methods.interpolation import InterpEnum
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceEnum
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeEnum
from hyo2.openbst.lib.processing.process_methods.source_level import SourceLevelEnum
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainEnum
from hyo2.openbst.lib.processing.process_methods.transmission_loss import TransmissionLossEnum
from hyo2.openbst.lib.processing.process_methods.tvg import TVGENUM

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# OPEN BST Project setup and file import
testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
bst = OpenBST(prj_name="cmp", force_new=True).prj

raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
cal_path = testing.download_data_folder().joinpath('calibration', 'chain_14m_200kHz.csv')
bst.add_raw(path=raw_path)
bst.add_calibration(path=cal_path)
bst.check_health()

# Import file using prr for manual comparison
infile = prr.x7kRead(str(str(raw_path)))
infile.mapfile(verbose=False)

# Extract data from the datafile
# - Get the sonar setting data
dg_type = '7000'
nr_dg_runtime = len(infile.map.packdir[dg_type])
# 39 is the number of fields in the runtime datagram
data_runtime = np.empty((nr_dg_runtime, 39), dtype=float)
for i in range(nr_dg_runtime):
    try:
        dg = infile.getrecord(dg_type, i)
        # this cast is dangerous
        data_runtime[i, :] = np.asarray(dg.header, dtype=float)

    except Exception:
        logger.error("Error while reading %s #%d" % (dg_type, i))

# - Get the receiver beam widths
dg_type = '7004'
nr_dg_beamgeo = len(infile.map.packdir[dg_type])
# -- determine how many rx beams system was set to. Assume constant through dg
dg = infile.getrecord(dg_type, 1)
nr_rx_beams = dg.header[1]
# -- reading all the 4 fields in the data section
data_beamgeo = np.empty((nr_dg_beamgeo, nr_rx_beams, 4))
for i in range(nr_dg_beamgeo):
    try:
        dg = infile.getrecord(dg_type, i)
        data_beamgeo[i, :, :] = dg.data.transpose()
    except Exception:
        logger.error("Error while reading %s #%d" % (dg_type, i))

# - Get the sonar bathy/Intensity data
dg_type = '7027'
nr_pings = len(infile.map.packdir[dg_type])

data_bathy = np.empty((nr_pings, nr_rx_beams, 7))  # 7 because of selecting some of the fields
data_bathy[:] = np.nan
time_bathy = np.empty(nr_pings)
time_bathy[:] = np.nan
for i in range(nr_pings):
    try:
        time_bathy[i] = infile.map.packdir[dg_type][i, 1]
        dg = infile.getrecord(dg_type, i)
        beam_indices = dg.data[:, 0].astype(int)
        data_bathy[i, beam_indices, 1:4] = dg.data[:, [1, 2, 6]]
        # change to avoid expensive matrix multiplication
        data_bathy[i, :, 0] = np.tile(np.array(dg.header[1], copy=True), nr_rx_beams)
        data_bathy[i, :, 4] = np.tile(np.array(dg.header[7], copy=True), nr_rx_beams)
        data_bathy[i, :, 5] = np.tile(np.array(dg.header[8], copy=True), nr_rx_beams)
        data_bathy[i, :, 6] = np.tile(np.array(dg.header[9], copy=True), nr_rx_beams)

    except Exception:
        logger.error("Error while reading %s #%d" % (dg_type, i))

# - Get the TVG
dg_type = '7010'
nr_dg_tvg = len(infile.map.packdir[dg_type])
data_tvg = list()
for i in range(nr_dg_tvg):
    try:
        dg = infile.getrecord(dg_type, i)
        data_tvg.append(dg.data)
    except Exception:
        logger.error("Error reading %s #%d" % (dg_type, i))

# - Get the position data
dg_type = '1003'
nr_dg_position = len(infile.map.packdir[dg_type])
time_position = np.empty(nr_dg_position)
position_measured = np.empty((nr_dg_position, 3))  # 3 because we read just 3 of the fields
for i in range(nr_dg_position):
    try:
        time_position[i] = infile.map.packdir[dg_type][i, 1]
        dg = infile.getrecord(dg_type, i)
        if dg.header[0] != 0:
            logger.debug("Warning: Datum is not WGS84")
        lat_rad, lon_rad = dg.header[2:4]
        height_datum = dg.header[4]
        lat_degree = np.rad2deg(lat_rad)
        lon_degree = np.rad2deg(lon_rad)
        position_measured[i, :] = [lat_degree, lon_degree, height_datum]
    except Exception:
        logger.error("Error reading %s #%d" % (dg_type, i))

# - Get the attitude data
# -- Get the roll, pitch, heave / Values are in radians
dg_type = '1012'
nr_dg_rph = len(infile.map.packdir[dg_type])
time_rph = np.empty(nr_dg_rph)
rph_measured = np.empty((nr_dg_rph, 3))
for i in range(nr_dg_rph):
    try:
        time_rph[i] = infile.map.packdir[dg_type][i, 1]
        dg = infile.getrecord(dg_type, i)
        rph_measured[i, :] = dg.header

    except Exception:
        logger.error("Error reading %s #%d" % (dg_type, i))

# -- Get the heading
dg_type = '1013'
nr_dg_heading = len(infile.map.packdir[dg_type])
time_heading = np.empty(nr_dg_heading)
heading_measured = np.empty(nr_dg_heading)
for i in range(nr_dg_heading):
    try:
        time_heading[i] = infile.map.packdir[dg_type][i, 1]
        dg = infile.getrecord(dg_type, i)
        heading_measured[i] = np.array(dg.header)

    except Exception:
        logger.error("Error reading %s #%d" % (dg_type, i))

# ----------------------------------------------------------------------------------------------------------------------
# Interp
lat_ping = np.interp(time_bathy, time_position, position_measured[:, 0], left=np.nan, right=np.nan)
lon_ping = np.interp(time_bathy, time_position, position_measured[:, 1], left=np.nan, right=np.nan)

roll_ping = np.interp(time_bathy, time_rph, rph_measured[:, 0], left=np.nan, right=np.nan)
pitch_ping = np.interp(time_bathy, time_rph, rph_measured[:, 1], left=np.nan, right=np.nan)
heave_ping = np.interp(time_bathy, time_rph, rph_measured[:, 2], left=np.nan, right=np.nan)
heading_ping = np.interp(time_bathy, time_heading, heading_measured[:], left=np.nan, right=np.nan)

bst.interpolation()

# Slant range
bottom_detect_sample = data_bathy[:, :, 1]
surface_sound_speed = data_runtime[:, 36]
sample_rate = data_bathy[:, :, 4]
range_prr = bottom_detect_sample / sample_rate * surface_sound_speed[:, np.newaxis] / 2

bst.parameters.raytrace.method_type = RayTraceEnum.slant_range_approximation
bst.raytrace()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['path_length']
range_bst = var[:]
print(np.allclose(range_bst, range_prr, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# Raw Decode
raw_decode_prr = 20 * np.log10(data_bathy[:, :, 3])
bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
bst.raw_decode()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
raw_decode_bst = var[:]
raw_decode_bst = raw_decode_bst.filled(fill_value=np.nan)
print(np.allclose(raw_decode_bst, raw_decode_prr, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# Static Gain
rx_fixed_gain = data_runtime[:, 15]
gst_prr = raw_decode_prr - rx_fixed_gain[:, np.newaxis]
bst.static_gain_correction()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
gst_bst = var[:]
gst_bst = gst_bst.filled(fill_value=np.nan)
print(np.allclose(gst_bst, gst_prr, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# TVG
tvg_gain = np.empty((nr_dg_tvg, nr_rx_beams))
for i in range(nr_dg_tvg):  # TODO: Make something better than a nested for loop
    for j in range(nr_rx_beams):
        if np.isnan(bottom_detect_sample[i, j]):
            tvg_gain[i, j] = np.nan
        else:
            # TODO: verify rounding logic
            tvg_index = int(np.round(bottom_detect_sample[i, j]))
            tvg_curve = data_tvg[i]
            tvg_gain[i, j] = tvg_curve[tvg_index]
tvg_prr = gst_prr - tvg_gain

bst.parameters.tvg.method_type = TVGENUM.gain_removal_tvg_curve_from_manufacturer
bst.tvg_gain_correction()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
tvg_bst = var[:]
tvg_bst = tvg_bst.filled(fill_value=np.nan)
# All true fails because bottom detect from snippet records has more nans than bottom detects from raw bathy
# replacing fields where bottom detects differ with nan
tvg_prr[np.isnan(tvg_bst)] = np.nan
print(np.allclose(tvg_bst, tvg_prr, atol=0.5, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# Source level
source_level = data_runtime[:, 14]
sl_prr = tvg_prr - source_level[:, np.newaxis]
bst.source_level_correction()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
sl_bst = var[:]
sl_bst = sl_bst.filled(fill_value=np.nan)
print(np.allclose(sl_bst, sl_prr, atol=0.5, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# Calibration
calibration_data = np.genfromtxt(fname=cal_path, dtype=float, delimiter=',', skip_header=2)

# -- Generate a 4th Order Fit to the curve data
poly_coefficents = np.polyfit(calibration_data[:, 0], calibration_data[:, 1], 4)
calibration_curve = np.arange(-75, 75, 0.1)[:, np.newaxis]
calibration_curve = np.tile(calibration_curve, [1, 2])
calibration_curve[:, 1] = np.polyval(poly_coefficents, calibration_curve[:, 0])

# -- Obtain Calibration Correction for each beam angle of each ping
rx_angle = data_bathy[:, :, 2]
calibration_correction = np.empty((nr_pings, nr_rx_beams))
for i in range(nr_pings):
    calibration_correction[i, :] = np.interp(np.rad2deg(rx_angle[i, :]),
                                             calibration_curve[:, 0], calibration_curve[:, 1])
# -- Apply calibration values
cl_prr = sl_prr - calibration_correction
bst.parameters.calibration.method_type = CalibrationEnum.calibration_file
bst.parameters.calibration.curve_order = 4
bst.parameters.calibration.fit_curve = True
bst.calibration()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
cl_bst = var[:]
cl_bst = cl_bst.filled(fill_value=np.nan)
print(np.allclose(cl_bst, cl_prr, atol=0.5, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# Transmission Loss
alpha = data_runtime[:, 35] / 1000
alpha = alpha[:, np.newaxis]
spreading_loss = 2* 20 * np.log10(range_prr)
absorp_loss = 2 * alpha * range_prr
transmission_loss = spreading_loss + absorp_loss
tl_prr = cl_prr + transmission_loss
bst.parameters.transmissionloss.method_type = TransmissionLossEnum.spherical
bst.parameters.transmissionloss.use_ssp = False
bst.transmission_loss_correction()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
tl_bst = var[:]
tl_bst = tl_bst.filled(fill_value=np.nan)
print(np.allclose(tl_bst, tl_prr, atol=0.5, equal_nan=True))
nc.close()
nc = None
grp = None
var = None

# Area Compensation
# - Correct for Ensonified Area
beamwidth_rx_across = data_beamgeo[:, :, 3]
beamwidth_tx_along = data_runtime[:, 20]
pulse_length = data_runtime[:, 6]
ind_zero = np.where(rx_angle == 0)
rx_angle[ind_zero[0], ind_zero[1]] = np.deg2rad(0.1)  # Nudge 0 values
area_beamlimited = beamwidth_rx_across * beamwidth_tx_along[:,
                                         np.newaxis] * range_prr ** 2  # TODO: Verify that the 7004 dg is accounting for the cosine of the angle
area_pulselimited = ((surface_sound_speed[:, np.newaxis] * pulse_length[:, np.newaxis]) / (
        2 * np.sin(np.abs(rx_angle)))) \
                    * (beamwidth_tx_along[:, np.newaxis] * range_prr)

# TODO: justify why taking the minimum
area_correction = 10 * np.log10(np.minimum(area_beamlimited, area_pulselimited))

# -- Correct the data
ac_prr = tl_prr - area_correction
bst.parameters.area_correction.method_type = AreaCorrectionEnum.flat_seafloor
bst.area_correction()
nc = Dataset(filename=bst.process.path.joinpath(bst.process.raw_process_list[0] + bst.process.ext), mode='a')
grp = nc.groups[bst.process.proc_manager.parent_process]
var = grp.variables['backscatter_data']
ac_bst = var[:]
ac_bst = ac_bst.filled(fill_value=np.nan)
print(np.allclose(ac_bst, ac_prr, atol=0.5, equal_nan=True))
nc.close()
nc = None
grp = None
var = None
logger.debug('point')
