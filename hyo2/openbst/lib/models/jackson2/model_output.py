import logging

logger = logging.getLogger(__name__)


class ModelOutput:

    def __init__(self):
        self.theta_g = None
        self.ss_tot = None
        self.ss_rough = None
        self.ss_vol = None
        self.ref_loss = None

