import logging
from hyo2.abc.lib.logging import set_logging

from hyo2.openbst.lib.models.jackson2.model import Model
from hyo2.openbst.lib.models.jackson2.model_plotter import ModelPlotter
from hyo2.openbst.lib.models.jackson2.dicts import TestSediments

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

plt = None
for sediment in TestSediments:

    mdl = Model()
    mdl.use_test_sed_params(sediment)
    mdl.use_default_mdl_params()
    logger.debug("model:\n%s" % mdl)
    plotter = ModelPlotter(mdl=mdl)
    plt = plotter.plot()

plt.show()
