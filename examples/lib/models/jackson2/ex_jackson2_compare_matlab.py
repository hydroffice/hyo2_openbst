import logging
import os
import scipy.io
import numpy as np

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.models.jackson2.model import Model
from hyo2.openbst.lib.models.jackson2.model_output import ModelOutput
from hyo2.openbst.lib.models.jackson2.model_plotter import ModelPlotter
from hyo2.openbst.lib.models.jackson2.dicts import TestSediments

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

use_300k = True

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir))
testing = Testing(root_folder=root_folder)
input_folder = testing.input_data_folder()
jackson2_folder = os.path.join(input_folder, "jackson2")
if use_300k:
    folder_freq = os.path.join(jackson2_folder, "300k")
else:
    folder_freq = os.path.join(jackson2_folder, "20k")
logger.debug("mat folder: %s" % folder_freq)

plt = None
for sediment in TestSediments:

    mdl = Model()
    mdl.use_test_sed_params(sediment)
    mdl.use_default_mdl_params()
    if use_300k:
        mdl.mdl_params.f = 300000
    mdl.run()
    logger.debug("theta_g: %s" % (mdl.out.theta_g.shape,))

    mat_folder = os.path.join(folder_freq, str(sediment).split('.')[-1].lower())
    logger.debug("mat folder: %s" % mat_folder)

    mat_files = Testing.files(mat_folder, ext='.mat')
    logger.debug("mat files: %d" % len(mat_files))

    mat_out = ModelOutput()

    for mat_file in mat_files:

        if "theta_g" in mat_file:
            mat_out.theta_g = scipy.io.loadmat(mat_file)['thetg'].flatten()
            logger.debug("%s: %s -> %s" % (os.path.basename(mat_file), mat_out.theta_g.shape,
                                           np.isclose(mat_out.theta_g, mdl.out.theta_g).all()))
        elif "ss_tot" in mat_file:
            mat_out.ss_tot = scipy.io.loadmat(mat_file)['sstot'].flatten()
            logger.debug("%s: %s -> %s" % (os.path.basename(mat_file), mat_out.ss_tot.shape,
                                           np.isclose(mat_out.ss_tot, mdl.out.ss_tot).all()))

        elif "ss_rough" in mat_file:
            mat_out.ss_rough = scipy.io.loadmat(mat_file)['ssrough'].flatten()
            logger.debug("%s: %s -> %s" % (os.path.basename(mat_file), mat_out.ss_rough.shape,
                                           np.isclose(mat_out.ss_rough, mdl.out.ss_rough).all()))

        elif "ss_vol" in mat_file:
            mat_out.ss_vol = scipy.io.loadmat(mat_file)['ssvol'].flatten()
            logger.debug("%s: %s -> %s" % (os.path.basename(mat_file), mat_out.ss_vol.shape,
                                           np.isclose(mat_out.ss_vol, mdl.out.ss_vol).all()))

        elif "ref_loss" in mat_file:
            mat_out.ref_loss = scipy.io.loadmat(mat_file)['refloss'].flatten()
            logger.debug("%s: %s -> %s" % (os.path.basename(mat_file), mat_out.ref_loss.shape,
                                           np.isclose(mat_out.ref_loss, mdl.out.ref_loss).all()))

        else:
            logger.debug("skip")

    # logger.debug("model:\n%s" % mdl)
    plotter = ModelPlotter(mdl=mdl)
    plt = plotter.plot(out_compare=mat_out)

plt.show()
