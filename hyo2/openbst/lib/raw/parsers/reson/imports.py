import logging

import numpy as np

from hyo2.openbst.lib.raw.parsers.reson.dg_formats import ResonDatagrams

# Data Type Extractions
def get_position(self):
    self.is_mapped()
    lat = list()
    lon = list()

    position = self.get_datagram(dg_type=ResonDatagrams.POSITION)
    times = [dg_pos.time for dg_pos in position]
    for dg_pos in position:
        if dg_pos.datum is "WGS":
            lat.append(dg_pos.latitude * (180 / np.pi))
            lon.append(dg_pos.longitude * (180 / np.pi))
        else:
            raise AttributeError("unrecognized datum: %s" % dg_pos.datum)
    # TODO: Write spatial reference check and formatter
    return times, lat, lon


def get_attitude(self):
    self.is_mapped()

    attitude = self.get_datagram(dg_type=ResonDatagrams.ROLLPITCHHEAVE)
    times_rph = [dg_att.time for dg_att in attitude]
    roll = np.rad2deg([dg_att.roll for dg_att in attitude])
    pitch = np.rad2deg([dg_att.pitch for dg_att in attitude])
    heave = np.rad2deg([dg_att.heave for dg_att in attitude])

    heading = self.get_datagram(dg_type=ResonDatagrams.HEADING)
    times_head = [dg_head.time for dg_head in heading]
    head = np.rad2deg([dg_head.heading for dg_head in heading])

    return times_rph, roll, pitch, heave, times_head, head