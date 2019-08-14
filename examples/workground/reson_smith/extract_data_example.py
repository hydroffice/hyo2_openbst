import os
import logging
import traceback
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import prr

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

# ----------- Get the sonar bathy/Intensity data -----------------
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

# ----------- Get the receiver beam widths -----------------------
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