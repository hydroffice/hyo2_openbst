import logging
from hyo2.abc.lib.logging import set_logging
from hyo2.openbst.lib.models.jackson2.sediment_params import SedimentParams
from hyo2.openbst.lib.models.jackson2.dicts import test_params

set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

params = SedimentParams()
logger.debug(params)

logger.debug("%s" % test_params)
