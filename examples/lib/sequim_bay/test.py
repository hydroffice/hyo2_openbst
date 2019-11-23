from PySide2 import QtWidgets
import os
import logging
from pathlib import Path
import traceback
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from hyo2.abc.lib.logging import set_logging
from hyo2.openbst.lib import prr

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# settings
map_verbose = False


def run(filename):
    if not os.path.exists(filename):
        raise RuntimeError("The passed file does not exist: %s" % filename)

    logger.debug("Raw data path: %s" % filename)
    infile = prr.x7kRead(filename)

    logger.debug("Mapping the raw data file ...")
    infile.mapfile(verbose=map_verbose)
    packet_types = infile.map.packdir.keys()
    logger.debug("Available packet types: %s" % (packet_types,))

    # set the packet type to read/plot
    pkt = '7027'
    nr_records = len(infile.map.packdir[pkt])
    print("Packet type: %s -> %d occurrences" % (pkt, nr_records))

    bs = None
    angle = None
    for n in range(nr_records):
        try:
            data = infile.getrecord(pkt, n)
            # data.display()  # prints the data and plots a graph if applicable

            if bs is None:  # first ping
                bs = data.data[:, -3].reshape(1, data.data[:, -3].size)
                angle = np.rad2deg(data.data[:, 2].reshape(1, data.data[:, 2].size))

            else:
                bs = np.concatenate((bs, data.data[:, -3].reshape(1, data.data[:, -3].size)))
                angle = np.concatenate((angle, np.rad2deg(data.data[:, 2].reshape(1, data.data[:, 2].size))))

        except Exception:
            logger.error(traceback.format_exc())
            logger.error("Error while reading packet %s #%d" % (pkt, n))

    logger.debug("retrieved pings x beams: %s" % (bs.shape,))

    # plot data

    # Determine data bounds
    index_beam = np.arange(100, 112, 1)
    # index_beam = np.array(50)
    # index_beam = None

    # Load and plot the calibration curve
    csv_path = Path(__file__).parent.joinpath(r'calibration_200kHz.csv')
    calibration_curve = np.genfromtxt(fname=csv_path, dtype=float, delimiter=',')
    plt.figure(0)
    plt.plot(calibration_curve[:,0], calibration_curve[:,1], linewidth=1.5, color='#d99d36')
    plt.grid()
    plt.xlabel('Incidence Angles [deg]')
    plt.ylabel('C [dB]')
    plt.title('Preliminary Calibration Curve - Reson T50-P @200kHz')

    # Intensity Mosaic
    plt.figure(1)
    plt.imshow(20*np.log10(bs), cmap='Greys_r')
    plt.xlabel('Beams [#]')
    plt.ylabel('Pings [#]')
    cbar = plt.colorbar()
    cbar.set_label('Digital Values [dB re arbitrary]')
    plt.title('Initial Raw Reflectivity - Reson T50-P @200kHz')

    # Determine if we have a single ping, range or all
    if index_beam is None:
        angles = angle[0, :]
        calibration_data = np.interp(angles, calibration_curve[:, 0], calibration_curve[:, 1])
        data_uncal = 20 * np.log10(bs.mean(axis=0))
        data_calibrated = data_uncal + calibration_data
    elif index_beam.size == 1:
        angles = angle[index_beam, :]
        calibration_data = np.interp(angles, calibration_curve[:, 0], calibration_curve[:, 1])
        data_uncal = 20*np.log10(bs[index_beam, :])
        data_calibrated = data_uncal + calibration_data

        # plot line where data is from
        plt.plot([0, angles.size-1], [index_beam, index_beam], linewidth=2, color='y')

    else:
        angles = angle[index_beam[0], :]
        calibration_data = np.interp(angles, calibration_curve[:, 0], calibration_curve[:, 1])
        data_uncal = 20*np.log10(bs[index_beam, :].mean(axis=0))
        data_calibrated = data_uncal + calibration_data

        # plot rectangle where data is from
        data_rect = patches.Rectangle((0, index_beam[0]), bs.shape[1], index_beam.size, linewidth=2,
                                      edgecolor='y', facecolor='none')
        plt.gca().add_patch(data_rect)

    # Plot figures
    fig = plt.figure(2)
    fig.suptitle('Correction of Data for System Directivity')
    plt.subplot(211)
    plt.plot(angles, data_uncal, linewidth=1.5, color='b')
    plt.grid()
    plt.ylabel('Digital Values [dB re Arbitrary]')
    plt.title('Uncorrected Data')

    plt.subplot(212)
    plt.plot(angles, data_calibrated, linewidth=1.5, color='b')
    plt.grid()
    plt.ylabel('Digital Values [dB re Arbitrary]')
    plt.xlabel('Incidence Angles [deg]')
    plt.title('Corrected Data')

    plt.figure(3)
    plt.plot(np.abs(angles[:int(angles.size/2):]), data_calibrated[:int(angles.size/2):],
             linewidth=1.5, color='#235b8c')
    plt.grid()
    # plt.xlim((0, self.numbeams))
    # plt.ylim((np.nanmax(self.data[1]), 0))
    plt.xlabel('Incidence Angles [deg]')
    plt.ylabel('Corrected Values [dB re Arbitrary]')
    plt.title('Angular Response Curve - Reson T50-P @200kHz')
    plt.draw()


if "__main__" == __name__:
    s7k_path = Path(__file__).parent.joinpath(r'20190321_185116.s7k')
    run(str(s7k_path))
    plt.ioff()  # turn off interactive more
    plt.show()  # stop the program from exiting until the plots are closed of the demo is killed.
    plt.ion()

overview = """The prr.py module, found at: %s
reads Reson data files into python data structures.""" % prr.__file__

