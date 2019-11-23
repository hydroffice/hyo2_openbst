import logging
from pathlib import Path
import traceback

from scipy import interpolate as interp_sp
import numpy as np
# noinspection PyUnresolvedReferences
from PySide2 import QtWidgets
import matplotlib.pyplot as mplt
from pyproj import Geod, Proj

from hyo2.openbst.lib import prr
from hyo2.openbst.lib.plotting.plots import Plots as oplts

logger = logging.getLogger(__name__)


def run(raw_input, calib_input):
    mplt.ioff()
    data_plt = oplts()

    # Open Data File and Map the datagrams
    infile = prr.x7kRead(str(raw_input))
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
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
            logger.error("Error reading %s #%d" % (dg_type, i))
    # -- Interpolate the position to the ping time
    lat_interp_object = interp_sp.interp1d(time_position, position_measured[:, 0], fill_value='extrapolate')
    lat_ping = lat_interp_object(time_bathy)

    lon_interp_object = interp_sp.interp1d(time_position, position_measured[:, 1], fill_value='extrapolate')
    lon_ping = lon_interp_object(time_bathy)

    # height_interp_object = interp_sp.interp1d(time_position, position_measured[:, 2], fill_value='extrapolate')
    # height_ping = height_interp_object(time_bathy)

    # data_position = np.array([lat_ping, lon_ping, height_ping])
    # data_position = data_position.transpose()

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
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
            logger.error("Error reading %s #%d" % (dg_type, i))

    # --Interpolate the attitude to the ping times
    # roll_interp_object = interp_sp.interp1d(time_rph, rph_measured[:, 0], fill_value='extrapolate')
    # roll_ping = roll_interp_object(time_bathy)
    #
    # pitch_interp_object = interp_sp.interp1d(time_rph, rph_measured[:, 1], fill_value='extrapolate')
    # pitch_ping = pitch_interp_object(time_bathy)
    #
    # heave_interp_object = interp_sp.interp1d(time_rph, rph_measured[:, 2], fill_value='extrapolate')
    # heave_ping = heave_interp_object(time_bathy)

    # TODO: Determine if extrapolate is good or bad
    heading_interp_object = interp_sp.interp1d(time_heading, heading_measured[:], fill_value='extrapolate')
    heading_ping = heading_interp_object(time_bathy)

    # data_attitude = np.array([roll_ping, pitch_ping, heading_ping, heave_ping])
    # data_attidude = data_attitude.transpose()

    # Processing Workflow
    # - Convert digital value to dB
    digital_value_db = 20 * np.log10(data_bathy[:, :, 3])

    # -- Plot the per beam reflectivity
    frequency = data_runtime[0, 3]
    title_str = "Initiial raw Relfectivity\n Reson T50-P @ %d kHz" % (frequency / 1000)
    fig_raw = data_plt.plot_ping_beam(digital_value_db, title=title_str)

    # - Calculate the estimated slant range
    bottom_detect_sample = data_bathy[:, :, 1]
    surface_sound_speed = data_runtime[:, 36]
    sample_rate = data_bathy[:, :, 4]
    range_m = bottom_detect_sample / sample_rate * surface_sound_speed[:, np.newaxis] / 2

    # -- Plot the range and check it's within reason
    cmap = 'gist_rainbow'
    title_str = "Preliminary Slant Range"
    clabel_str = "Range [m]"
    fig_range = data_plt.plot_ping_beam(range_m, colormap=cmap, title=title_str, clabel=clabel_str)

    # - Remove the static gain
    rx_fixed_gain = data_runtime[:, 15]
    datacorr_fixed_gain = digital_value_db - rx_fixed_gain[:, np.newaxis]

    # -- Plot the adjusted gain
    title_str = "Static Gain [%.1f dB] Correction Product\nReson T50-P @ %d kHz" % (rx_fixed_gain[0], frequency/1000)
    fig_fixedgain = data_plt.plot_ping_beam(datacorr_fixed_gain, title=title_str)

    # - Remove the TVG
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

    alpha = data_runtime[:, 35] / 1000
    spreading = data_runtime[:, 37]
    tvg_bswg = (spreading[:, np.newaxis] * np.log10(range_m)) + 2 * (alpha[:, np.newaxis] * range_m)
    datacorr_tvg_gain = digital_value_db - tvg_gain

    # -- Plot a comparison between the calculated and estimated tvg values
    mplt.figure()
    mplt.plot(np.nanmean(tvg_gain, axis=0))
    mplt.plot(np.nanmean(tvg_bswg, axis=0))
    mplt.grid()
    mplt.title(
        "Comparison between RESON TVG and BSWG TVG\nSpreading = %d dB / Absorption = %0.2f dB/m"
        % (spreading[0], alpha[0]))
    mplt.xlabel("Beam [#]")
    mplt.ylabel("Average TVG value [dB}")
    mplt.legend(["Reson TVG", "BSWG TVG"])

    # -- Plot the corrected values using the reson tvg
    title_str = "TVG Correction Product\nReson T50-P @ %dHz" % (frequency/1000)
    fig_tvgcorr = data_plt.plot_ping_beam(datacorr_tvg_gain, title=title_str)
    mplt.imshow(datacorr_tvg_gain, cmap='Greys_r')

       # - Correct for the Source Level
    source_level = data_runtime[:, 14]
    datacorr_sourcelevel = datacorr_tvg_gain - source_level[:, np.newaxis]

    # -- Plot the corrected values
    title_str = "Source Level Correction Product\nReson T50-P @ %dkHz" % (frequency / 1000)
    fig_sourcelevel = data_plt.plot_ping_beam(datacorr_sourcelevel, title=title_str)

    # - Apply Relative Calibration Correction
    # -- Load calibration curve
    calibration_data = np.genfromtxt(fname=calib_input, dtype=float, delimiter=',')

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
    datacorr_echolevel = datacorr_sourcelevel - calibration_correction

    # -- Plot the corrected values
    title_str = "Echo Level Product\nReson T50-P @ %dkHz" % (frequency/1000)
    clabel_str = "Intensity Value [dB re 1$mu$Pa]"
    fig_echo = data_plt.plot_ping_beam(datacorr_echolevel, title=title_str, clabel=clabel_str)

    # - Correct for the Transmission Loss
    # TODO: current assumption is spherical spreading
    transmission_loss = 40 * np.log10(range_m) + 2 * (alpha[:, np.newaxis] / 1000) * range_m
    datacorr_transmissionloss = datacorr_sourcelevel + transmission_loss

    # -- Plot the corrected values10
    title_str = "Transmission Loss Correction Product\nReson T50-P @ %dkHz" % (frequency/1000)
    clabel_str = "Intensity Value [dB re 1$mu$Pa]"
    fig_transmission = data_plt.plot_ping_beam(datacorr_transmissionloss, title=title_str, clabel=clabel_str)

    # - Correct for Ensonified Area
    # -- Calculate the Ensonified area using a flat seafloor assumption
    beamwidth_rx_across = data_beamgeo[:, :, 3]
    beamwidth_tx_along = data_runtime[:, 20]
    pulse_length = data_runtime[:, 6]
    ind_zero = np.where(rx_angle == 0)
    rx_angle[ind_zero[0], ind_zero[1]] = np.deg2rad(0.1)  # Nudge 0 values
    area_beamlimited = beamwidth_rx_across * beamwidth_tx_along[:,
                                             np.newaxis] * range_m ** 2  # TODO: Verify that the 7004 dg is accounting for the cosine of the angle
    area_pulselimited = ((surface_sound_speed[:, np.newaxis] * pulse_length[:, np.newaxis]) / (
            2 * np.sin(np.abs(rx_angle)))) \
                        * (beamwidth_tx_along[:, np.newaxis] * range_m)

    # TODO: justify why taking the minimum
    area_correction = 10 * np.log10(np.minimum(area_beamlimited, area_pulselimited))

    # -- Correct the data
    datacorr_radiometric = datacorr_transmissionloss - area_correction

    # -- Plot area regions
    fig_areacorr = mplt.figure()
    mplt.plot(10 * np.log10(np.nanmean(area_beamlimited, axis=0)))
    mplt.plot(10 * np.log10(np.nanmean(area_pulselimited, axis=0)))
    mplt.plot(10 * np.log10(np.nanmean(np.minimum(area_pulselimited, area_beamlimited), axis=0)))
    mplt.grid(which='minor')
    mplt.xlabel("Beam [#]")
    mplt.ylabel("Area Correction [dB]")
    mplt.title("Comparison of Area Corrections")

    # Plot the area corrected data
    title_str = "Seafloor Backscatter Product\nReson T50-P @ %dkHz" % (frequency/1000)
    clabel_str = r'$S(\theta)_b$  [dB re $1\mu$Pa]'
    fig_radiometric = data_plt.plot_ping_beam(datacorr_radiometric, title=title_str, clabel=clabel_str)

    # Make an ARA like curve
    # - Determine the mean for all beams over a small ping interval [20 pings]
    ara_curve = datacorr_radiometric[100:120, :].mean(axis=0)
    angles = np.rad2deg(rx_angle[100, :])
    fig_ara = mplt.figure()
    mplt.plot(angles, ara_curve, linewidth=2, color='#235b8c')
    mplt.xlabel("Incidence Angles [deg]")
    mplt.ylabel(r"Backscatter Stength [dB re 1$\mu$Pa")
    mplt.title('Full Swath ARA Curve\nReson T50-P @200kHz')

    # Geo-reference Data
    geo = Geod(ellps='WGS84')
    # TODO: add geo_to_utm_zone()
    utm = Proj(proj='utm', zone=10, ellps='WGS84', preserve_units=False)
    # ----------- Determine the beam  xyz postion using slant range ------
    #   Ship Ref                    Geo Ref
    #       | x+                        | n+
    #       |                           |
    #       |                           |
    # ------------- y+              -------- e+

    # - Determine x,y,z in ship reference frame
    # TODO: use proper georefencing
    y_shiprf = range_m * np.sin(rx_angle)  # Negative rx angles are portside
    x_shiprf = np.zeros(y_shiprf.shape)
    z = range_m * np.cos(rx_angle)

    # - Determine x,y,z in geographic reference frame (meters) relative to ship
    azimuth = np.tile(heading_ping[:, np.newaxis], nr_rx_beams)
    nn_georf = np.empty((nr_pings, nr_rx_beams))
    ee_georf = np.empty((nr_pings, nr_rx_beams))

    for j in range(nr_pings):  # TODO: Another terrible for loop that should become something else
        for i in range(nr_rx_beams):
            if np.isnan(x_shiprf[j, i]):
                nn_georf[j, i] = np.nan
                ee_georf[j, i] = np.nan
            else:
                rot = np.array([[np.cos(azimuth[j, i]), -np.sin(azimuth[j, i])],
                                [np.sin(azimuth[j, i]), np.cos(azimuth[j, i])]])
                nn_georf[j, i], ee_georf[j, i] = rot @ [x_shiprf[j, i], y_shiprf[j, i]]

    # - Determine the UTM position of each ping
    lon_in = np.tile(lon_ping[:, np.newaxis], nr_rx_beams)
    lat_in = np.tile(lat_ping[:, np.newaxis], nr_rx_beams)
    ee_ping, nn_ping = utm(lon_in, lat_in)
    ee_beam = ee_ping + ee_georf
    nn_beam = nn_ping + nn_georf

    # - Create regular grid
    # TODO: This section hurts my soul. There has to be a much better way to grid data.
    # Prep data
    data_linear = 10 ** (np.ndarray.flatten(datacorr_radiometric) / 10)
    ee_data = np.ndarray.flatten(ee_beam)
    nn_data = np.ndarray.flatten(nn_beam)

    # -- Determine the grid extents and pad -> [left, bottom, right, top]
    ee_min = np.floor(np.nanmin(ee_data)) - 50
    nn_min = np.floor(np.nanmin(nn_data)) - 50
    ee_max = np.ceil(np.nanmax(ee_data)) + 50
    nn_max = np.ceil(np.nanmax(nn_data)) + 50
    #
    # -- Create coordinate arrays
    bin_size = 1.
    # ee_range = np.arange(ee_min, ee_max + bin_size, bin_size)
    # nn_range = np.arange(nn_min, nn_max + bin_size, bin_size)
    # ee_grid, nn_grid = np.meshgrid(ee_range, nn_range)
    #
    # -- Make blank grid
    data_grid = np.zeros((int((nn_max - nn_min) / bin_size) + 1, int((ee_max - ee_min) / bin_size) + 1))
    # data_grid[:] = np.nan
    grid_count = np.copy(data_grid)

    # -- Fill in the grid
    for i in range(data_linear.size):
        if np.isnan(data_linear[i]):
            continue
        row = int((nn_data[i] - nn_min) / bin_size)
        col = int((ee_data[i] - ee_min) / bin_size)

        data_grid[row, col] += data_linear[i]
        grid_count[row, col] += 1

    mask = grid_count == 0
    georef_grid = np.empty_like(data_grid)
    georef_grid[mask] = np.nan
    georef_grid[~mask] = 10 * np.log10(data_grid[~mask] / grid_count[~mask])

    # - Plot the data
    mplt.figure()
    mplt.imshow(georef_grid, cmap='Greys_r', origin='lower', aspect='equal')
    mplt.colorbar()
    mplt.ioff()  # TODO: Determine the proper backend settings for the project
    mplt.show()


if __name__ == '__main__':

    raw_path = Path(__file__).parents[3].joinpath('data', 'download', 'reson', '20190321_185116.s7k')
    if not raw_path.exists():
        raise RuntimeError("unable to locate: %s" % raw_path)

    calib_path = Path(__file__).parents[3].joinpath('data', 'download', 'reson', 'chain_14m_200kHz.csv')
    if not calib_path.exists():
        raise RuntimeError("unable to locate: %s" % calib_path)

    run(raw_input=raw_path, calib_input=calib_path)
