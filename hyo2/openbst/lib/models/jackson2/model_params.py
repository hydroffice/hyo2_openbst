import logging

logger = logging.getLogger(__name__)


class ModelParams:

    def __init__(self):
        self.f = 20000.0  # frequency [Hz]
        self.c_w = 1500.0  # compressional wave speed in water [m/s]

        # bi-static angles
        self.bi_theta_i = 20.0  # grazing angle of incident acoustic energy in water [deg]
        self.bi_theta_s = 20.0  # grazing angle of scattered acoustic energy in water [deg]
        self.bi_phi_s = 180.0  # azimuthal angle of scattered acoustic energy in water [deg]

        self.sigma_0 = 0.1  # max allowed volume scattering contribution to effective interface scattering strength

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "    <frequency: %s Hz>\n" % self.f
        msg += "    <sound speed in water: %s m/s>\n" % self.c_w

        msg += "    <grazing angle of incidence: %s deg>\n" % self.bi_theta_i
        msg += "    <grazing angle of scattering: %s deg>\n" % self.bi_theta_s
        msg += "    <azimuth of scattering: %s>\n" % self.bi_phi_s

        msg += "    <sigma 0: %s>\n" % self.sigma_0

        return msg
