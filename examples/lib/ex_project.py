import logging

from hyo2.openbst.lib.project import Project

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)


prj = Project()
logger.debug("\n%s" % prj)
