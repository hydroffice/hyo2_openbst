from PySide2 import QtWidgets
import os
import logging
import traceback
import matplotlib.pyplot as plt
from hyo2.abc.lib.logging import set_logging
from hyo2.openbst.lib import prr

set_logging(ns_list=["hyo2.openbst", ])
# logger = logging.get_logger(__name__)


def run(filename):
    infile = prr.x7kRead(filename)
    print("Mapping the file, this can be slow -- please wait...")
    infile.mapfile(verbose=False)  # find where the data packets are and keep track so we can read them quickly later
    packet_types = infile.map.packdir.keys()
    print("packet types in file:", packet_types)
    packet_types = ['7027', ]  # '1012', '7503', '7000', '7006']
    # show the first occurrence of each packet type
    for pkt in packet_types:
        numrecords = len(infile.map.packdir[pkt])
        print("\n\nFor packet type:", pkt, ":")
        print("  There were %d occurrences\n" % numrecords)
        try:
            data = infile.getrecord(pkt, 0)
            data.display()  # prints the data and plots a graph if applicable
        except Exception as e:
            print(traceback.format_exc())
            print("Error reading packet of type: ", pkt)
            print("Packet may not be supported yet ", pkt)

    d = infile.getrecord(1012, 0)  # this is an attitude record
    print("For data packets, the header data is accessible by index or name")
    print("\nAll data packets have a get_display_string and display method available.\nSome have a plot function too, display will automatically call it.")
    print("\n\nHere is everything available:")
    print(dir(d))  # show that data fields (like heave roll pitch) are accessible directly


if "__main__" == __name__:
    file_path = r'C:\PythonCode\hyo2_openbst\examples\lib\sequim_bay\20190321_185116.s7k'
    # f = os.path.join(os.path.dirname(__file__), r"003_1535.7K")
    run(file_path)
    plt.ioff()  # turn off interactive more
    plt.show()  # stop the program from exiting until the plots are closed of the demo is killed.
    plt.ion()

overview = """The prr.py module, found at: %s
reads Reson data files into python data structures.""" % prr.__file__

