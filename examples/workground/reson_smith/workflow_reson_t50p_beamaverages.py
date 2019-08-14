from PySide2 import QtWidgets

import os
import logging
import traceback
from pathlib import Path, PurePath

from scipy import interpolate as interp_sp
import numpy as np
import matplotlib.pyplot as plt

from pyproj import Geod, Proj

from hyo2.openbst.lib import prr

logger = logging.getLogger(__name__)


def run(filneame):
    # ************************** Open Data File and Map the datagrams **************************************************
    infile = prr.x7kRead(str(filneame))
    infile.mapfile(verbose=False)

    # ************************** Extract data from the datafile ********************************************************
    # ----------- Get the sonar setting data -------------------------
    pkt = '7000'
    num_records_runtime = len(infile.map.packdir[pkt])
    data_runtime = np.empty((num_records_runtime, 39), dtype=float)
    for n in range(num_records_runtime):
        try:
            record = infile.getrecord(pkt, n)
            data_runtime[n, :] = np.asarray(record.header, dtype=float)

        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error while reading %s #%d" % (pkt, n))

    # ----------- Get the receiver beam widths -----------------------
    pkt = '7004'
    num_records_beamgeo = len(infile.map.packdir[pkt])
    # determine how many rx beams system was set to. Assume constant through record
    record = infile.getrecord(pkt, 1)
    number_rx_beams = record.header[1]

    data_beamgeo = np.empty((num_records_beamgeo, number_rx_beams, 4))
    for n in range(num_records_beamgeo):
        try:
            record = infile.getrecord(pkt, n)
            data_beamgeo[n, :, :] = record.data.transpose()
        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error while reading %s #%d" % (pkt, n))

    # ----------- Get the sonar bathy/Intensity data -----------------
    pkt = '7027'
    num_pings = len(infile.map.packdir[pkt])
    data_bathy = np.empty((num_pings, number_rx_beams, 7))
    data_bathy[:] = np.nan
    time_bathy = np.empty(num_pings)
    for n in range(num_pings):
        try:
            time_bathy[n] = infile.map.packdir[pkt][n, 1]
            if n == 15:
                logger.debug("debug")
            record = infile.getrecord(pkt, n)
            inds = record.data[:, 0].astype(int)
            if inds.size != number_rx_beams:
                logger.debug(f"Ping {n}")
            data_bathy[n, inds, 1:4] = record.data[:, [1, 2, 6]]
            data_bathy[n, :, 0] = np.tile(np.array(record.header[1], copy=True), number_rx_beams)
            data_bathy[n, :, 4] = np.tile(np.array(record.header[7], copy=True), number_rx_beams)
            data_bathy[n, :, 5] = np.tile(np.array(record.header[8], copy=True), number_rx_beams)
            data_bathy[n, :, 6] = np.tile(np.array(record.header[9], copy=True), number_rx_beams)

        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error while reading %s #%d" % (pkt, n))

    # ----------- Get the TVG ----------------------------------------
    pkt = '7010'
    num_records_tvg = len(infile.map.packdir[pkt])
    data_tvg = list()
    for n in range(num_records_tvg):
        try:
            record = infile.getrecord(pkt, n)
            data_tvg.append(record.data)
        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error reading %s #%d" % (pkt, n))

    # ----------- Get the position data ------------------------------
    pkt = '1003'
    num_records_position = len(infile.map.packdir[pkt])
    time_position = np.empty((num_records_position))
    position_measured = np.empty((num_records_position, 3))
    for n in range(num_records_position):
        try:
            time_position[n] = infile.map.packdir[pkt][n, 1]
            record = infile.getrecord(pkt, n)
            if record.header[0] != 0:
                logger.debug("Warning: Datum is not WGS84")
            lat_rad, lon_rad = record.header[2:4]
            height_datum = record.header[4]
            lat_degeee = np.rad2deg(lat_rad)
            lon_degree = np.rad2deg(lon_rad)
            position_measured[n, :] = [lat_degeee, lon_degree, height_datum]
        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error reading %s #%d" % (pkt, n))
    # Interpolate the position to the ping time
    lat_interp_object = interp_sp.interp1d(time_position, position_measured[:, 0], fill_value='extrapolate')
    lat_ping = lat_interp_object(time_bathy)

    lon_interp_object = interp_sp.interp1d(time_position, position_measured[:, 1], fill_value='extrapolate')
    lon_ping = lon_interp_object(time_bathy)

    height_interp_object = interp_sp.interp1d(time_position, position_measured[:, 2], fill_value='extrapolate')
    height_ping = height_interp_object(time_bathy)

    data_position = np.array([lat_ping, lon_ping, height_ping])
    data_position = data_position.transpose()

    # ----------- Get the attitude data ------------------------------
    # Get the roll, pitch, heave / Values are in radians
    pkt = '1012'
    num_records_rph = len(infile.map.packdir[pkt])
    time_rph = np.empty(num_records_rph)
    rph_measured = np.empty((num_records_rph, 3))
    for n in range(num_records_rph):
        try:
            time_rph[n] = infile.map.packdir[pkt][n, 1]
            record = infile.getrecord(pkt, n)
            rph_measured[n, :] = record.header

        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error reading %s #%d" % (pkt, n))

    # Get the heading
    pkt = '1013'
    num_records_heading = len(infile.map.packdir[pkt])
    time_heading = np.empty(num_records_heading)
    heading_measured = np.empty(num_records_heading)
    for n in range(num_records_heading):
        try:
            time_heading[n] = infile.map.packdir[pkt][n, 1]
            record = infile.getrecord(pkt, n)
            heading_measured[n] = np.array(record.header)

        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error reading %s #%d" % (pkt, n))

    # Interpolate the attitude to the ping times
    roll_interp_object = interp_sp.interp1d(time_rph, rph_measured[:, 0], fill_value='extrapolate')
    roll_ping = roll_interp_object(time_bathy)

    pitch_interp_object = interp_sp.interp1d(time_rph, rph_measured[:, 1], fill_value='extrapolate')
    pitch_ping = pitch_interp_object(time_bathy)

    heave_interp_object = interp_sp.interp1d(time_rph, rph_measured[:, 2], fill_value='extrapolate')
    heave_ping = heave_interp_object(time_bathy)

    heading_interp_object = interp_sp.interp1d(time_heading, heading_measured[:], fill_value='extrapolate')
    heading_ping = heading_interp_object(time_bathy)

    data_attitude = np.array([roll_ping, pitch_ping, heading_ping, heave_ping])
    data_attidude = data_attitude.transpose()

    # ************************** Processing Workflow *******************************************************************
    # ----------- Convert digital value to dB ------------------------
    digital_value_db = 20 * np.log10(data_bathy[:, :, 3])

    # Plot the per beam reflectivity
    fig_digital_image = plt.figure()
    plt.imshow(digital_value_db, cmap='Greys_r')
    plt.title("Initial Raw Reflectivity\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Digital Intensity Value [dB re arbitrary]")

    # ----------- Calculate the estimated slant range ----------------
    bottom_detect_sample = data_bathy[:, :, 1]
    surface_sound_speed = data_runtime[:, 36]
    sample_rate = data_bathy[:, :, 4]
    range_m = bottom_detect_sample / sample_rate * surface_sound_speed[:, np.newaxis] / 2

    # Plot the range and check it's within reason (QPS data says the depth is around 21-22m along this line)
    fig_range = plt.figure()
    plt.imshow(range_m, cmap='gist_rainbow')
    plt.title("Estimated Slant Range")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Range [m]")

    # ----------- Remove the static gain -----------------------------
    rx_fixed_gain = data_runtime[:, 15]
    datacorr_fixed_gain = digital_value_db - rx_fixed_gain[:, np.newaxis]

    # Plot the adjusted gain
    fig_fixedgain = plt.figure()
    plt.imshow(datacorr_fixed_gain, cmap='Greys_r')
    plt.title(f"Static Gain [{rx_fixed_gain[0]}] Correction Product\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Digital Intensity Value [dB re arbitrary]")

    # ----------- Remove the TVG -------------------------------------
    tvg_gain = np.empty((num_records_tvg, number_rx_beams))

    for n in range(num_records_tvg):  # TODO: Make something better than a nested for loop
        for m in range(number_rx_beams):
            if np.isnan(bottom_detect_sample[n, m]):
                tvg_gain[n, m] = np.nan
            else:
                ind = int(np.round(bottom_detect_sample[n, m]))
                tvg_curve = data_tvg[n]
                tvg_gain[n, m] = tvg_curve[ind]

    alpha = data_runtime[:, 35] / 1000
    spreading = data_runtime[:, 37]
    tvg_bswg = (spreading[:, np.newaxis] * np.log10(range_m)) - 2 * (alpha[:, np.newaxis] * range_m)
    datacorr_tvg_gain = digital_value_db - tvg_gain

    # Plot a comparison between the calculated and estimated tvg values
    fig_tvg_compare = plt.figure()
    plt.plot(np.nanmean(tvg_gain, axis=0))
    plt.plot(np.nanmean(tvg_bswg, axis=0))
    plt.grid()
    plt.title(
        f"Comparison between the RESON TVG values and the BSWG Values \n Spreading = {spreading[0]}dB / Absorption = "
        f"{alpha[0]}dB/m")
    plt.xlabel("Beam [#]")
    plt.ylabel("Average TVG value [dB}")
    plt.legend(["Reson TVG", "BSWG TVG"])

    # Plot the corrected values using the reson tvg
    fig_tvgcorr = plt.figure()
    plt.imshow(datacorr_tvg_gain, cmap='Greys_r')
    plt.title("TVG Correction Product\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Digital Intensity Value [dB re arbitrary]")

    # ----------- Apply Relative Calibration Correction --------------
    # Load calibration curve
    csv_path = Path(__file__).parent.joinpath(r'chain_14m_200kHz.csv')
    calibration_data = np.genfromtxt(fname=csv_path, dtype=float, delimiter=',')

    # Generate a 4th Order Fit to the curve data
    poly_coefficents = np.polyfit(calibration_data[:, 0], calibration_data[:, 1], 4)
    calibration_curve = np.arange(-75, 75, 0.1)[:, np.newaxis]
    calibration_curve = np.tile(calibration_curve, [1, 2])
    calibration_curve[:, 1] = np.polyval(poly_coefficents, calibration_curve[:, 0])

    # Obtain Calibration Correction for each beam angle of each ping
    rx_angle = data_bathy[:, :, 2]
    calibration_correction = np.empty((num_pings, number_rx_beams))
    for n in range(num_pings):
        calibration_correction[n, :] = np.interp(np.rad2deg(rx_angle[n, :]),
                                                 calibration_curve[:, 0], calibration_curve[:, 1])
    # Apply calibration values
    datacorr_echolevel = datacorr_tvg_gain - calibration_correction

    # Plot the corrected values
    fig_echo = plt.figure()
    plt.imshow(datacorr_echolevel, cmap='Greys_r')
    plt.title("Echo Level Product\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Intensity Value [dB re 1$mu$Pa]")

    # ----------- Correct for the Source Level -----------------------
    source_level = data_runtime[:, 14]
    datacorr_sourcelevel = datacorr_echolevel - source_level[:, np.newaxis]

    # Plot the corrected values
    fig_sourcelevel = plt.figure()
    plt.imshow(datacorr_sourcelevel, cmap='Greys_r')
    plt.title("Source Level Correction Product\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Intensity Value [dB re 1$mu$Pa]")

    # ----------- Correct for the Transmission Loss ------------------
    transmission_loss = 40 * np.log10(range_m) + 2 * (alpha[:, np.newaxis] / 1000) * range_m
    datacorr_transmissionloss = datacorr_sourcelevel + transmission_loss

    # Plot the corrected values
    fig_sourcelevel = plt.figure()
    plt.imshow(datacorr_transmissionloss, cmap='Greys_r')
    plt.title("Transmission Loss Correction Product\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Intensity Value [dB re 1$mu$Pa]")

    # ----------- Correct for Ensonified Area ------------------------
    # Calculate the Ensonified area using a flat seafloor assumption
    beamwidth_rx_across = data_beamgeo[:, :, 3]
    beamwidth_tx_along = data_runtime[:, 20]
    pulse_length = data_runtime[:, 6]
    ind_zero = np.where(rx_angle == 0)
    rx_angle[ind_zero[0], ind_zero[1]] = np.deg2rad(0.1)  # Nudge 0 values
    area_beamlimited = beamwidth_rx_across * beamwidth_tx_along[:,
                                             np.newaxis] * range_m ** 2  # TODO: Verify that the 7004 record is accounting for the cosine of the angle
    area_pulselimited = ((surface_sound_speed[:, np.newaxis] * pulse_length[:, np.newaxis]) / (
            2 * np.sin(np.abs(rx_angle)))) \
                        * (beamwidth_tx_along[:, np.newaxis] * range_m)

    area_correction = 10 * np.log10(np.minimum(area_beamlimited, area_pulselimited))

    # Correct the data
    datacorr_radiometric = datacorr_transmissionloss - area_correction

    # Plot the area correction data
    fig_areacorr = plt.figure()
    plt.plot(10 * np.log10(np.nanmean(area_beamlimited, axis=0)))
    plt.plot(10 * np.log10(np.nanmean(area_pulselimited, axis=0)))
    plt.plot(10 * np.log10(np.nanmean(np.minimum(area_pulselimited, area_beamlimited), axis=0)))
    plt.grid(which='minor')
    plt.xlabel("Beam [#]")
    plt.ylabel("Area Correction [dB]")
    plt.title("Comparison of Area Corrections")

    # Plot the corrected data
    fig_radiometric = plt.figure()
    plt.imshow(datacorr_radiometric, cmap='Greys_r')
    plt.title("Seafloor Backscatter Product\nReson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label(r'$S(\theta)_b$  [dB re $1\mu$Pa]')

    # ----------- Make an ARA like curve -----------------------------
    # Determine the mean for all beams over a small ping interval [20 pings]
    ara_curve = datacorr_radiometric[100:120, :].mean(axis=0)
    angles = np.rad2deg(rx_angle[100, :])
    fig_ara = plt.figure()
    plt.plot(angles, ara_curve, linewidth=2, color='#235b8c')
    plt.xlabel("Incidence Angles [deg]")
    plt.ylabel(r"Backscatter Stength [dB re 1$\mu$Pa")
    plt.title('Full Swath ARA Curve\nReson T50-P @200kHz')

    # ************************** Geo-reference Data ********************************************************************
    geo = Geod(ellps='WGS84')
    utm = Proj(proj='utm', zone=19, ellps='WGS84', preserve_units=False)
    # ----------- Determine the beam  xyz postion using slant range ------
    #   Ship Ref                    Geo Ref
    #       |   x+                      |   n+
    #       |                           |
    #       |                           |
    # ------------- y+              -------- e+

    # Determine x,y,z in ship reference frame
    y_shiprf = range_m * np.sin(rx_angle)  # Negative rx angles are portside
    x_shiprf = np.zeros(y_shiprf.shape)
    z = range_m * np.cos(rx_angle)

    # Determine x,y,z in geographic reference frame (meters) relative to ship
    azimuth = np.tile(heading_ping[:, np.newaxis], number_rx_beams)
    nn_georf = np.empty((num_pings, number_rx_beams))
    ee_georf = np.empty((num_pings, number_rx_beams))

    for m in range(num_pings):  # TODO: Another terrible for loop that should become something else
        for n in range(number_rx_beams):
            if np.isnan(x_shiprf[m, n]):
                nn_georf[m, n] = np.nan
                ee_georf[m, n] = np.nan
            else:
                rot = np.array([[np.cos(azimuth[m, n]), -np.sin(azimuth[m, n])],
                                [np.sin(azimuth[m, n]), np.cos(azimuth[m, n])]])
                nn_georf[m, n], ee_georf[m, n] = rot @ [x_shiprf[m, n], y_shiprf[m, n]]

    # Determine the UTM position of each ping
    lon_in = np.tile(lon_ping[:, np.newaxis], number_rx_beams)
    lat_in = np.tile(lat_ping[:, np.newaxis], number_rx_beams)
    ee_ping, nn_ping = utm(lon_in, lat_in)
    ee_beam = ee_ping + ee_georf
    nn_beam = nn_ping + nn_georf

    # ----------- Create regular grid --------------------------------
    # TODO: This section hurts my soul. There has to be a much better way to grid data.
    # Prep data
    data_linear = 10 ** (np.ndarray.flatten(datacorr_radiometric) / 10)
    ee_data = np.ndarray.flatten(ee_beam)
    nn_data = np.ndarray.flatten(nn_beam)

    # Determine the grid extents and pad -> [left, bottom, right, top]
    ee_min = np.floor(np.nanmin(ee_data)) - 50
    nn_min = np.floor(np.nanmin(nn_data)) - 50
    ee_max = np.ceil(np.nanmax(ee_data)) + 50
    nn_max = np.ceil(np.nanmax(nn_data)) + 50
    #
    # # Create coordinate arrays
    bin_size = 0.5
    # ee_range = np.arange(ee_min, ee_max + bin_size, bin_size)
    # nn_range = np.arange(nn_min, nn_max + bin_size, bin_size)
    # ee_grid, nn_grid = np.meshgrid(ee_range, nn_range)
    #
    # # Make blank grid
    data_grid = np.zeros((int((nn_max-nn_min)/bin_size)+1, int((ee_max-ee_min)/bin_size)+1))
    # data_grid[:] = np.nan
    grid_count = np.copy(data_grid)

    # # Fill in the grid
    # for n in range(np.alen(data_linear)):
    #     if np.isnan(data_linear[n]):
    #         continue
    #
    #     ee_diff = np.abs(ee_grid - ee_data[n])
    #     nn_diff = np.abs(nn_grid - nn_data[n])
    #     ibin = np.logical_and(ee_diff < bin_size / 2, nn_diff < bin_size / 2)
    #     ind_bin = np.where(ibin == True)
    #
    #     data_grid[ind_bin[0][0], ind_bin[1][0]] += data_linear[n]
    #     grid_count[ind_bin[0][0], ind_bin[1][0]] += 1
    for n in range(data_linear.size):
        if np.isnan(data_linear[n]):
            continue
        row = int((nn_data[n] - nn_min)/bin_size)
        col = int((ee_data[n] - ee_min)/bin_size)

        data_grid[row, col] += data_linear[n]
        grid_count[row, col] += 1

    mask = grid_count == 0
    georef_grid = np.empty_like(data_grid)
    georef_grid[mask] = np.nan
    georef_grid[~mask] = 10*np.log10(data_grid[~mask]/grid_count[~mask])

    fig_georef = plt.figure()
    plt.imshow(georef_grid,cmap='Greys_r',origin='lower')
    plt.colorbar()
    logger.debug('debug')


if __name__ == '__main__':
    filepath = Path(__file__).parents[3].joinpath(PurePath(r'data/input/reson/20190730_144835.s7k'))

    ara = run(filepath)
    plt.ioff()
    plt.show()
    plt.ion()
