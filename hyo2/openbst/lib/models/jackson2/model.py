import numpy as np
import math
import cmath
from typing import Optional
import logging

# from hyo.arch.common.helper import Helper
from hyo2.openbst.lib.models.jackson2.model_output import ModelOutput
from hyo2.openbst.lib.models.jackson2.model_params import ModelParams
from hyo2.openbst.lib.models.jackson2.sediment_params import SedimentParams
from hyo2.openbst.lib.models.jackson2.dicts import TestSediments, test_params

logger = logging.getLogger(__name__)


class Model:

    def __init__(self, mdl_params: Optional[ModelParams] = None,
                 sed_params: Optional[SedimentParams] = None):
        self._mp = mdl_params  # model parameters
        self._sp = sed_params  # sediment parameters

        # internal data
        self.a_p = None  # ratio of complex compressional wave speed to sound speed of overlying water [no-dim]
        self.a_t = None  # ratio of complex shear wave speed to sound speed of overlying water [no-dim]
        self.omega = None  # angular frequency [rad/s]
        self.k_w = None  # acoustic wave number in water [1/m]
        self.q_0 = None  # volume fluctuation inverse correlation scale [1/m]
        self.phi_s = None  # azimuthal angle of scattered acoustic energy in water [deg]

        self.out = ModelOutput()

    @property
    def sed_params(self):
        return self._sp

    @sed_params.setter
    def sed_params(self, params):
        if not isinstance(params, SedimentParams):
            raise Exception("invalid type for passed Sediment Parameters: %s" % type(params))
        self._sp = params

    def use_test_sed_params(self, test_sediment):
        if test_sediment not in TestSediments:
            raise Exception("invalid test sediment: %s" % test_sediment)
        self._sp = test_params[test_sediment]

    @property
    def mdl_params(self):
        return self._mp

    @mdl_params.setter
    def mdl_params(self, params):
        if not isinstance(params, ModelParams):
            raise Exception("invalid type for passed Model Parameters: %s" % type(params))
        self._mp = params

    def use_default_mdl_params(self):
        self._mp = ModelParams()

    def run(self):
        if self._sp is None:
            raise RuntimeError("first set the Sediment Parameters")
        if self._mp is None:
            raise RuntimeError("first set the Model Parameters")

        self.a_p = self._sp.nu_p / complex(1, self._sp.delta_p)  # 8.47
        self.a_t = self._sp.nu_t / complex(1, self._sp.delta_t)  # 8.48

        self.omega = 2.0 * math.pi * self._mp.f
        self.k_w = self.omega / self._mp.c_w
        self.q_0 = 0.001 * self.k_w

        self.phi_s = 180.0

        self.out.theta_g = np.arange(1.0, 90.0 + 1.0, 1.0)  # + 1.0 to include 90.0 def
        # logger.debug("theta g: %s" % (self.out.theta_g, ))
        self.out.theta_i = np.arange(89.0, -1.0, -1.0)  # + 1.0 to include 90.0 def
        # logger.debug("theta i: %s" % (self.out.theta_i,))

        self.out.ss_tot = np.zeros_like(self.out.theta_g)
        self.out.ss_rough = np.zeros_like(self.out.theta_g)
        self.out.ss_vol = np.zeros_like(self.out.theta_g)
        self.out.ref_loss = np.zeros_like(self.out.theta_g)

        for idx in range(self.out.theta_g.size):

            theta_i = self.out.theta_g[idx]
            theta_s = theta_i

            sigma_s, ref = self._ss_rough2_00(theta_i, theta_s)
            sigma_v = self._ss_vol2_00(theta_i, theta_s)
            # limit volume scattering cross-section to values less than sigma_0
            sigma_v = 1.0 / (1.0/self._mp.sigma_0 + 1.0/sigma_v)

            # logger.debug(sigma_s)
            # logger.debug(ref)
            # logger.debug("sigma_v: %s" % sigma_v)

            self.out.ss_tot[idx] = 10.0 * math.log10(sigma_s.real + sigma_v)
            self.out.ss_rough[idx] = 10.0 * math.log10(sigma_s.real)
            self.out.ss_vol[idx] = 10.0 * math.log10(sigma_v)
            self.out.ref_loss[idx] = -20.0 * math.log10(abs(ref))

        return True

    def _ss_rough2_00(self, theta_i, theta_s):
        """Small-slope elastic roughness scattering cross section and reflection coefficient
        using equations in tm2-00"""

        # logger.debug("theta_i: %s, theta_s: %s" % (theta_i, theta_s))

        # Cosines and sine of grazing angles in water
        cos_w_i = math.cos(math.radians(theta_i))
        sin_w_i = math.sin(math.radians(theta_i))
        cos_w_s = math.cos(math.radians(theta_s))
        sin_w_s = math.sin(math.radians(theta_s))
        cos_phi = math.cos(math.radians(self.phi_s))
        sin_phi = math.sin(math.radians(self.phi_s))

        # P - proportional to complex sine of angles in sediment
        p_p_i = cmath.sqrt(self.a_p ** -2 - cos_w_i ** 2)
        p_p_s = cmath.sqrt(self.a_p ** -2 - cos_w_s ** 2)
        p_t_i = cmath.sqrt(self.a_t ** -2 - cos_w_i ** 2)
        p_t_s = cmath.sqrt(self.a_t ** -2 - cos_w_s ** 2)

        # cos and sin of double shear propagation angles in sediment
        cos_2_t_i = 2 * self.a_t ** 2 * cos_w_i ** 2 - 1
        sin_2_t_i = cmath.sqrt(1 - cos_2_t_i ** 2)
        cos_2_t_s = 2 * self.a_t ** 2 * cos_w_s ** 2 - 1
        sin_2_t_s = cmath.sqrt(1 - cos_2_t_s ** 2)

        # impedance
        z_i = self._sp.a_rho * sin_w_i * (cos_2_t_i ** 2 / p_p_i + sin_2_t_i ** 2 / p_t_i)
        z_s = self._sp.a_rho * sin_w_s * (cos_2_t_s ** 2 / p_p_s + sin_2_t_s ** 2 / p_t_s)

        # reflection coefficients
        gamma_i = (z_i - 1)/(z_i + 1)
        gamma_s = (z_s - 1)/(z_s + 1)
        ref = gamma_i

        # transverse wave-number change
        q = self.k_w * cmath.sqrt(cos_w_s ** 2 - 2 * cos_w_s * cos_w_i * cos_phi + cos_w_i ** 2 + 0.001 ** 2)

        # vertical wave-number change
        q3 = self.k_w * (sin_w_s + sin_w_i)

        # cosine of angle between Ki and Ks
        s = cos_w_s * cos_w_i * cos_phi

        # Structure function parameters

        alpha = self._sp.gamma_2 / 2 - 1
        ch2 = (2 * math.pi * self._sp.w_2 * math.gamma(2 - alpha) * 2 ** (-2 * alpha)) / \
              (alpha * (1 - alpha) * math.gamma(1 + alpha))

        # Parameter needed for small-slope approximation
        p = 0.5 * ch2 * q3 ** 2 * q ** (-2 * alpha)

        # Compute factors multiplying various combinations of (1+-gamms)*(1+-gammi)

        # Factor multip;ying (1+gamms)*(1+gammi)

        d1 = -1 + s + 1/(self.a_p**2 * self._sp.a_rho * cos_2_t_s * cos_2_t_i) \
             - self.a_t**2 * ((self.a_t**(-2) - 2 * cos_w_s**2 - 2 * cos_w_i**2 + 2 * s) * s
                              + 2 * cos_w_s ** 2 * cos_w_i **2)/(self._sp.a_rho * cos_2_t_s * cos_2_t_i)

        # Factor multiplying (1-gamms)*(1+gammi)

        d2 = -4 * self.a_t**4 * sin_w_s * p_t_s / \
             (cos_2_t_s * cos_2_t_i) * (p_p_i ** 2 * cos_w_s ** 2 + (cos_w_i**2 - s) * s)

        # Factor multiplying (1+gamms)*(1-gammi)

        d3 = -4 * self.a_t ** 4 * sin_w_i * p_t_i / \
             (cos_2_t_s * cos_2_t_i) * (p_p_s**2 * cos_w_i**2 + (cos_w_s**2 - s) * s)

        # Factor multiplying (1-gamms)*(1-gammi)

        d4 = 2 * self.a_t ** 6 * self._sp.a_rho * sin_w_s * sin_w_i * p_t_s * p_t_i / (cos_2_t_s * cos_2_t_i) * \
             (2 * (self.a_t**(-2) - 2*s) * s - 4 * cos_w_i**2 * cos_w_s**2 * (1 - 2 * self.a_t**2 * self.a_p ** (-2))) \
             - (self._sp.a_rho - 1) * sin_w_s * sin_w_i

        # Factor from perturbation theory cross section
        a = 0.5 * self.k_w ** 2 * \
            (d1 * (1 + gamma_s) * (1 + gamma_i) + d2 * (1 - gamma_s) * (1 + gamma_i) +
             d3*(1 + gamma_s) * (1 - gamma_i) + d4 * (1 - gamma_s) * (1 - gamma_i))

        # Computation of bistatic scattering strength
        y = self._q_int_prony(alpha, p)

        sigma_s = abs(a) ** 2 / (2 * math.pi * q**2 * q3**2) * y

        return sigma_s, ref

    def _q_int_prony(self, alpha, q):
        """Prony approximation to Kirchhoff scattering integral: int ( J0(u) exp (-q*u^(2*alpha)) u du )"""

        epsilon = 0.001  # Smallest value of exponential in fitted region
        umax = (1 / q * abs(math.log(epsilon))) ** (1 / (2 * alpha))  # Corresponding value of u
        nu = 100  # Number of values in u-series
        nterm = 10  # Number of terms in Prony series

        if alpha == 0.5:

            y = 1 / q**2 * (1 + q**(-2))**(-1.5)

        elif alpha == 1:

            y = math.exp(-1 / (4 * q)) / (2 * q)

        else:

            u = np.linspace(0, umax.real, nu)
            # logger.debug("alpha: %s" % alpha)
            # logger.debug("u: %s" % u)
            del_u = umax.real / (nu - 1)
            # logger.debug("delu: %s" % del_u)

            w_val = np.exp(-q.real * np.power(u, 2*alpha)).reshape((-1, 1))
            # logger.debug("w_val: %s" % w_val)

            nterm, s = self._prony2(nterm, 0, del_u, w_val)

            # y = real(sum(s(1:nterm,1)./(s(1:nterm,2).^2.*(1+s(1:nterm,2).^(-2)).^1.5)))
            y = np.real(
                    np.sum(
                        s[:nterm, 0] / (
                            np.multiply(
                                np.power(s[:nterm, 1], 2),
                                np.power(
                                    1 + np.power(s[:nterm, 1], -2),
                                    1.5
                                )
                            )
                        )
                    )
                )
            # logger.debug("y: %s" % y)

        return y

    def _prony2(self, nterm, z0, dz, wval):
        # Expands the uniformly sampled complex function w(z) into
        # a series of weighted exponentials by Prony's method.
        # The Prony procedure is in two parts. In the first part, the
        # complex exponents are obtained. Next, the weighting
        # coefficents are obtained in a standard linear-regression
        # procedure.
        # REVISED TO REMOVE UNSTABLE POLES

        m1, m2 = wval.shape
        # logger.debug("shape: %s %s" % (m1, m2))
        if m1 < 2*nterm:
            raise Exception("Prony2 with insufficient number of samples: %d < %d" % (m1, 2*nterm))
        if m2 != 1:
            raise Exception("Prony2 only operates with column vectors")

        # Determine the exponents.
        bvec = -wval[nterm:m1]
        # logger.debug("bvec: %s" % (bvec.shape,))
        nequ = m1 - nterm
        n1 = nequ
        a_mat = np.zeros((nequ, nterm))
        # logger.debug("n1: %s" % n1)
        for i1 in range(nterm):
            a_mat[:, i1] = wval[i1:i1+n1].T
        # logger.debug("a_mat: %s" % a_mat)

        c = np.linalg.lstsq(a_mat, bvec, rcond=None)[0]
        c = np.flipud(c)
        c = np.insert(c, 0, 1.0, axis=0)
        # logger.debug("c: %s" % c)
        u = np.roots(c.flatten())
        # logger.debug("u: %s" % u)

        # Find Bi from Ui, scaling for a non-unit interval.
        # Note, the assumed translation which set z0=0 manifests
        # itself only in the weighting coefficints

        b = np.log(u) / dz
        # logger.debug("b: %s" % (b.shape, ))

        unst = np.where(np.real(b) > 0)[0]
        Nun = unst.size
        # logger.debug("unst: %s, Nun: %s" % (unst, Nun))
        if Nun > 0:
            u[unst] = []  # FIXME: this seems to be unused
            nterm = nterm - unst.size

        # Find weighting coefficients Ai through linear regression.
        z = np.linspace(z0, z0 + (m1 - 1) * dz, m1).T
        # logger.debug("z: %s" % z)

        a_mat = np.exp(np.outer(z, b))
        # logger.debug("a_mat: %s" % a_mat)
        a = np.linalg.lstsq(a_mat, wval, rcond=None)[0]
        # logger.debug("a: %s" % (a.shape,))
        wtest = np.dot(a_mat, a)
        werr = wtest - wval
        errsq = np.dot(werr.T, werr)
        wvalsq = np.dot(wval.T, wval)
        rms = np.sqrt(errsq / wvalsq)
        rcd1 = 0
        rcd2 = 0

        s_c0 = np.vstack((a, rcd2, rms))
        s_c1 = np.vstack((b.reshape((-1, 1)), rcd1, 0))
        s = np.hstack((s_c0, s_c1))
        # logger.debug("s: %s" % s)
        return nterm, s

    def _ss_vol2_00(self, theta_i, theta_s):

        # logger.debug("theta_i: %s, theta_s: %s" % (theta_i, theta_s))

        # Cosines and sine of grazing angles in water
        cos_w_i = math.cos(math.radians(theta_i))
        sin_w_i = math.sin(math.radians(theta_i))
        cos_w_s = math.cos(math.radians(theta_s))
        sin_w_s = math.sin(math.radians(theta_s))
        cos_phi = math.cos(math.radians(self.phi_s))
        sin_phi = math.sin(math.radians(self.phi_s))

        # P - proportional to complex sine of angles in sediment
        p_i_1 = cmath.sqrt(self.a_p ** -2 - cos_w_i ** 2)
        p_s_1 = cmath.sqrt(self.a_p ** -2 - cos_w_s ** 2)
        p_i_2 = cmath.sqrt(self.a_t ** -2 - cos_w_i ** 2)
        p_s_2 = cmath.sqrt(self.a_t ** -2 - cos_w_s ** 2)

        # cos and sin of double shear propagation angles in sediment
        cos_2_t_i = 2 * self.a_t ** 2 * cos_w_i ** 2 - 1
        sin_2_t_i = cmath.sqrt(1 - cos_2_t_i ** 2)
        cos_2_t_s = 2 * self.a_t ** 2 * cos_w_s ** 2 - 1
        sin_2_t_s = cmath.sqrt(1 - cos_2_t_s ** 2)

        # impedances
        z_i = self._sp.a_rho * sin_w_i * (cos_2_t_i ** 2 / p_i_1 + sin_2_t_i ** 2 / p_i_2)
        z_s = self._sp.a_rho * sin_w_s * (cos_2_t_s ** 2 / p_s_1 + sin_2_t_s ** 2 / p_s_2)

        # reflection coefficients
        gamma_i_w = (z_i - 1)/(z_i + 1)
        gamma_s_w = (z_s - 1)/(z_s + 1)

        # transmission coefficients
        gamma_i_1 = cos_2_t_i * sin_w_i / p_i_1 * (1 - gamma_i_w)
        gamma_i_2 = sin_2_t_i * sin_w_i / p_i_2 * (1 - gamma_i_w)
        gamma_s_1 = cos_2_t_s * sin_w_s / p_s_1 * (1 - gamma_s_w)
        gamma_s_2 = sin_2_t_s * sin_w_s / p_s_2 * (1 - gamma_s_w)

        # Various propagation and polarization vectors
        # Here 1 = p, 2 = t, 3 = v.  down = "-", up = "+"

        # First, redefine
        a_1 = self.a_p
        a_2 = self.a_t
        a_3 = self.a_t

        # Column vectors in a 3x3 matrix
        b_down = np.array([
            [cos_w_i, cos_w_i, p_i_2],
            [0, 0, 0],
            [-p_i_1, -p_i_2, cos_w_i]
        ])
        # logger.debug("b_down:\n%s" % b_down)
        b_up = np.array([
            [cos_w_s * cos_phi, cos_w_s * cos_phi, -p_s_2 * cos_phi],
            [cos_w_s * sin_phi, cos_w_s * sin_phi, -p_s_2 * sin_phi],
            [p_s_1, p_s_2, cos_w_s]
        ])
        # logger.debug("b_up:\n%s" % b_up)

        b = np.zeros_like(b_down)
        for na in range(3):
            for nb in range(3):
                b[na, nb] = np.dot(b_up[:, na].T, b_down[:, nb])
        # logger.debug("b:\n%s" % b)

        # Various matrices. 1 = pp, 2 = pt, 3 = tp, 4 = tt
        q = np.zeros((3, 4), dtype=np.complex)
        q3 = np.zeros((4, 1), dtype=np.complex)
        w = np.zeros((4, 1), dtype=np.complex)
        for n1 in range(2):
            for n2 in range(2):
                if (n1 == 0) and (n2 == 0):
                    eta = 0
                elif (n1 == 0) and (n2 == 1):
                    eta = 1
                elif (n1 == 1) and (n2 == 0):
                    eta = 2
                else:
                    eta = 3

                q[:, eta] = np.dot(self.k_w, b_up[:, n1] - b_down[:, n2])
                if n1 == 0:
                    if n2 == 0:
                        q3[eta, 0] = np.dot(self.k_w, p_s_1 + p_i_1)
                        w[eta, 0] = np.dot(gamma_s_1, gamma_i_1)
                    else:  # n2 == 1
                        q3[eta, 0] = np.dot(self.k_w, p_s_1 + p_i_2)
                        w[eta, 0] = np.dot(gamma_s_1, gamma_i_2)
                else:  # n1 == 1
                    if n2 == 0:
                        q3[eta, 0] = np.dot(self.k_w, p_s_2 + p_i_1)
                        w[eta, 0] = np.dot(gamma_s_2, gamma_i_1)
                    else:  # n2 == 1
                        q3[eta, 0] = np.dot(self.k_w, p_s_2 + p_i_2)
                        w[eta, 0] = np.dot(gamma_s_2, gamma_i_2)

        # logger.debug("q:\n%s" % q)
        # logger.debug("q3:\n%s" % q3)
        # logger.debug("w:\n%s" % w)

        # A 4x3 matrix.  The column index is 1 = density, 2 = comp., 3 = shear
        d_rho_p = np.zeros((4, 1), dtype=np.complex)
        d_rho_p[0] = np.power(self.a_p, -2) - b[0, 0]
        d_rho_p[1] = b[0, 2]
        d_rho_p[2] = -b[2, 0]
        d_rho_p[3] = b[2, 2]
        d_p = np.zeros((4, 1), dtype=np.complex)
        d_p[0] = 2.0 * np.power(self.a_p, -2)
        d_t = np.zeros((4, 1), dtype=np.complex)
        d_t_multi = 2.0 * np.power(self.a_t, 2)
        d_t[0] = d_t_multi * 2.0 * (np.power(b[0, 0], 2) - np.power(self.a_p, -4))
        d_t[1] = d_t_multi * -2.0 * b[0, 2] * b[0, 1]
        d_t[2] = d_t_multi * 2.0 * b[2, 0] * b[1, 0]
        d_t[3] = d_t_multi * -b[2, 2] * b[1, 1] - b[2, 1] * b[1, 2]
        # logger.debug("d_rho_p:\n%s" % d_rho_p)
        # logger.debug("d_p:\n%s" % d_p)
        # logger.debug("d_t:\n%s" % d_t)
        d = np.hstack([d_rho_p + d_t / 2.0, d_p, d_t])
        # logger.debug("d:\n%s" % d)

        # The final two sums giving the cross section
        sigmav = 0.0
        for n1 in range(4):
            for n2 in range(4):
                q_bragg = 0.5 * (q[:, n1] + np.conj(q[:, n2]))
                # logger.debug("q_bragg:\n%s" % q_bragg)
                big_w = self._vol_spect(q_bragg)
                # logger.debug("big_w:\n%s" % big_w)

                # Combine D and the fluctuation matrix to make
                # D(n1,n3)*conj(D(n2,n4))*fluct(n3,n4) summed over n3,n4 =1:3
                pp = np.dot(np.dot(d[n1, :], self._sp.fluct), d[n2, :].conj().T)
                # logger.debug("+:\n%s" % d[n1, :])
                # logger.debug("++:\n%s" % np.dot(d[n1, :], self._sp.fluct))
                # logger.debug("+++:\n%s" % d[n2, :].T)
                # logger.debug("pp:\n%s" % pp)
                # logger.debug("w[n1]:\n%s" % w[n1])
                # logger.debug("**:\n%s" % np.dot(w[n1], np.conj(w[n2])))
                # logger.debug("***:\n%s" % np.dot(np.dot(w[n1], np.conj(w[n2])), pp))
                sigmav_imag_num = np.dot(np.dot(np.dot(w[n1], np.conj(w[n2])), pp), big_w)
                # logger.debug("sigmav_imag_num:\n%s" % (sigmav_imag_num,))
                sigmav_imag_den = (q3[n1] - np.conj(q3[n2]))
                # logger.debug("sigmav_imag_den:\n%s" % (sigmav_imag_den,))
                sigmav_imag = sigmav_imag_num / sigmav_imag_den
                # logger.debug("sigmav_imag:\n%s" % (sigmav_imag,))
                sigmav += np.imag(sigmav_imag)[0]

        sigmav = -0.5 * math.pi * self.k_w ** 4.0 * self._sp.a_rho ** 2 * sigmav
        return sigmav

    def _vol_spect(self, q_bragg):
        q2 = q_bragg[0] ** 2 + q_bragg[1] ** 2
        return self._sp.w_3 / (self._sp.aspect ** 2 * q2 + q_bragg[2] ** 2 + self.q_0 ** 2) ** (self._sp.gamma_3 / 2.0)

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        if self._mp is None:
            msg += "  <mod params: %s>\n" % self._mp
        else:
            msg += "  %s" % self._mp

        if self._sp is None:
            msg += "  <sed params: %s>\n" % self._sp
        else:
            msg += "  %s" % self._sp

        msg += "  <a_p: %s>\n" % self.a_p
        msg += "  <a_t: %s>\n" % self.a_t

        msg += "  <omega: %s>\n" % self.omega
        msg += "  <k_w: %s>\n" % self.k_w
        msg += "  <q_0: %s>\n" % self.q_0

        msg += "  <phi_s: %s>\n" % self.phi_s

        return msg
