from PySide2 import QtWidgets
import os
import logging
import traceback
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hyo2.openbst.lib import prr
from hyo2.abc.lib.logging import set_logging

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)


def run(filneame):
    infile = prr.x7kRead(filneame)
    infile.mapfile(verbose=False)

    # Get the sonar setting data
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

    # Get the sonar bathy/Intensity data
    pkt = '7027'
    num_records_bathy = len(infile.map.packdir[pkt])
    data_bathy = np.empty((num_records_bathy, 256, 7))
    for n in range(num_records_bathy):
        try:
            record = infile.getrecord(pkt, n)
            data_bathy[n, :, 0] = np.tile(np.array(record.header[1], copy=True), 256)
            data_bathy[n, :, 1:4] = record.data[:, [1, 2, 6]]
            data_bathy[n, :, 4] = np.tile(np.array(record.header[7], copy=True), 256)
            data_bathy[n, :, 5] = np.tile(np.array(record.header[8], copy=True), 256)
            data_bathy[n, :, 6] = np.tile(np.array(record.header[9], copy=True), 256)

        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error while reading %s #%d" % (pkt, n))

    # Get the receiver beam widths
    pkt = '7004'
    num_records_beam = len(infile.map.packdir[pkt])
    data_beamgeo = np.empty((num_records_bathy, 256, 4))
    for n in range(num_records_beam):
        try:
            record = infile.getrecord(pkt, n)
            data_beamgeo[n, :, :] = record.data.transpose()
        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error while reading %s #%d" % (pkt, n))

    # Get the apparent TVG that doesn't match the calculation I made based off the spreading and absoption values
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

    # Now lets calculate the ARA
    # First calculate the estimated range
    detect_sample = data_bathy[:, :, 1]
    sound_speed = data_runtime[:, 36]
    sample_rate = data_bathy[:, :, 4]
    range_m = detect_sample / sample_rate * sound_speed[:, np.newaxis] / 2

    # First remove the static gain and TVG
    rx_fixed_gain = data_runtime[:, 15]
    tvg_gain = np.empty((num_records_tvg, 256))
    for n in range(num_records_tvg):  # TODO: Make something better than a nested for loop
        for m in range(256):
            ind = int(np.round(detect_sample[n, m]))
            tvg_curve = data_tvg[n]
            tvg_gain[n, m] = tvg_curve[ind]

    # spreading = data_runtime[:, 37]       # TODO: Figure out why a simple TL loss model doesn't match TVG values
    alpha = data_runtime[:, 35]
    digital_value = 20 * np.log10(data_bathy[:, :, 3])
    # ara_data = digital_value - rx_fixed_gain[:, np.newaxis] -
    # spreading[:, np.newaxis]*np.log10(range_m) - 2 * alpha[:, np.newaxis]/1000 * range_m
    data_intermediate = digital_value - rx_fixed_gain[:, np.newaxis] - tvg_gain

    # Now lets correct for the Manufacturer Modifications
    # No manufacturer corrections

    # Correct for transmit/receive sensitivities
    # Load calibration curve
    csv_path = Path(__file__).parent.joinpath(r'chain_14m_200kHz.csv')
    calibration_curve = np.genfromtxt(fname=csv_path, dtype=float, delimiter=',')

    rx_angle = data_bathy[:, :, 2]
    calibration_correction = np.empty((num_records_bathy, 256))
    for n in range(num_records_bathy):
        calibration_correction[n, :] = np.interp(np.rad2deg(rx_angle[n, :]),
                                                 calibration_curve[:, 0], calibration_curve[:, 1])

    data_ara = data_intermediate - calibration_correction

    # Correct for the Source Level
    source_level = data_runtime[:, 14]
    data_ara = data_ara - source_level[:, np.newaxis]

    # Correct for Transmission Loss
    transmission_loss = 40 * np.log10(range_m) + 2 * (alpha[:, np.newaxis] / 1000) * range_m
    data_ara = data_ara + transmission_loss

    # Correct for Ensonified Area
    beamwidth_rx_across = data_beamgeo[:, :, 3]
    beamwidth_tx_along = data_runtime[:, 20]
    pulse_length = data_runtime[:, 6]
    ind_zero = np.where(rx_angle == 0)
    rx_angle[ind_zero[0], ind_zero[1]] = np.deg2rad(0.1)  # Nudge 0 values
    area_beamlimited = beamwidth_rx_across * beamwidth_tx_along[:,
                                             np.newaxis] * range_m ** 2  # TODO: Verify that the 7004 record is accounting for the cosine of the angle
    area_pulselimited = ((sound_speed[:, np.newaxis] * pulse_length[:, np.newaxis]) / (2 * np.sin(np.abs(rx_angle)))) \
                        * (beamwidth_tx_along[:, np.newaxis] * range_m)

    area_correction = 10 * np.log10(np.minimum(area_beamlimited, area_pulselimited))
    data_ara = data_ara - area_correction

    # Plot some of the imagery
    fig1 = plt.figure()
    plt.imshow(digital_value, cmap='Greys_r')
    plt.title("Initial Raw Reflectivity - Reson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Digital Intensity Value [dB re arbitrary]")


    fig2 = plt.figure()
    plt.imshow(data_intermediate, cmap='Greys_r')
    plt.title("Intermediate Intensity Product - Reson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label("Digital Intensity Value [dB re arbitrary]")

    fig3 = plt.figure()
    plt.imshow(data_ara, cmap='Greys_r')
    plt.title("Seafloor Scattering Strength - Reson T50-P @ 200kHz")
    plt.xlabel("Beam [#]")
    plt.ylabel("Ping [#]")
    cbar = plt.colorbar()
    cbar.set_label(r'$S(\theta)_b$  [dB re $1\mu$Pa]')

    # Make an ARA from some ping averages
    ara_curve = data_ara[100:113, :].mean(axis=0)
    angles = np.rad2deg(rx_angle[100, :])
    fig4 = plt.figure()
    plt.plot(angles, ara_curve, linewidth=2, color='#235b8c')
    plt.xlabel("Incidence Angles [deg]")
    plt.ylabel(r"Backscatter Stength [dB re 1$\muPa$")
    plt.title('Full Swath ARA Curve - Reson T50-P @200kHz')
    


    logger.debug('Debug spot')
    return data_ara


if __name__ == '__main__':
    filepath = r'C:\PythonCode\hyo2_openbst\examples\lib\sequim_bay\20190321_185116.s7k'

    ara = run(filepath)
    plt.ioff()
    plt.show()
    plt.ion()
