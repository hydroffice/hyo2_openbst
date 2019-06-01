import logging

logger = logging.getLogger(__name__)


class PlotParams:

    def __init__(self, db_min=-80.0, db_max=20.0):
        self.db_min = db_min
        self.db_max = db_max
        self.db_range = self.db_max - self.db_min

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "    <dB min: %s>\n" % self.db_min
        msg += "    <dB max: %s>\n" % self.db_max
        msg += "    <dB range: %s>\n" % self.db_range

        return msg
