import numpy as np
import logging

logger = logging.getLogger(__name__)


class SedimentParams:

    def __init__(self):
        self.name = "Unknown"

        self.a_rho = 0.0  # ratio of sediment density to density of overlying water

        self.nu_p = 0.0  # ratio of compressional wave speed to sound speed of overlying water
        self.delta_p = 0.0  # loss parameter for compressional wave

        self.nu_t = 0.0  # ratio of shear wave speed to sound speed of overlying water
        self.delta_t = 0.0  # loss parameter for shear wave

        self.gamma_2 = 0.0  # spectral exponent for roughness
        self.w_2 = 0.0  # spectral strength for roughness

        self.gamma_3 = 0.0  # spectral exponent for volume heterogeneity
        self.w_3 = 0.0  # spectral strength for volume heterogeneity
        self.aspect = 0.0  # aspect ratio / anisotropy parameter for volume heterogeneity

        self.fluct = np.zeros([3, 3], dtype=np.float64)  # fluctuation matrix

    # _______________________________________________________________________________
    # ############################## AUXILIARY METHODS ##############################

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "    <name: %s>\n" % self.name

        msg += "    <a_rho: %f>\n" % self.a_rho

        msg += "    <nu_p: %f>\n" % self.nu_p
        msg += "    <delta_p: %f>\n" % self.delta_p

        msg += "    <nu_t: %f>\n" % self.nu_t
        msg += "    <delta_t: %f>\n" % self.delta_t

        msg += "    <gamma_2: %f>\n" % self.gamma_2
        msg += "    <w_2: %s>\n" % self.w_2

        msg += "    <gamma_3: %f>\n" % self.gamma_3
        msg += "    <w_3: %f>\n" % self.w_3

        msg += "    <aspect: %f>\n" % self.aspect
        msg += "    <fluct: %s>\n" % self.fluct.tolist()

        return msg
