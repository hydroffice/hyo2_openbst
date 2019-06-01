import numpy as np
from collections import OrderedDict
from enum import Enum
import logging
from hyo2.openbst.lib.models.jackson2.sediment_params import SedimentParams

logger = logging.getLogger(__name__)


class TestSediments(Enum):
    ROUGH_ROCK = 0
    ROCK = 1
    COBBLE = 2
    SANDY_GRAVEL = 3
    COARSE_SAND = 4
    MEDIUM_SAND = 5
    FINE_SAND = 6
    SILT = 7


def make_test_params_dict():
    test_dicts = OrderedDict()

    for sediment in TestSediments:
        test_dicts[sediment] = SedimentParams()

        if sediment == TestSediments.ROUGH_ROCK:

            test_dicts[sediment].name = 'Rough Rock'
            test_dicts[sediment].color = '#00CED1'

            test_dicts[sediment].a_rho = 2.5

            test_dicts[sediment].nu_p = 2.3
            test_dicts[sediment].delta_p = 0.00174

            test_dicts[sediment].nu_t = 1.3
            test_dicts[sediment].delta_t = 0.085

            test_dicts[sediment].gamma_2 = 2.75
            test_dicts[sediment].w_2 = 0.0001

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.0002
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 3, 4],
                                                   [3, 9, 12],
                                                   [4, 12, 16]])

        elif sediment == TestSediments.ROCK:

            test_dicts[sediment].name = 'Rock'
            test_dicts[sediment].color = '#696969'

            test_dicts[sediment].a_rho = 2.5

            test_dicts[sediment].nu_p = 2.3
            test_dicts[sediment].delta_p = 0.00174

            test_dicts[sediment].nu_t = 1.31
            test_dicts[sediment].delta_t = 0.085

            test_dicts[sediment].gamma_2 = 3.0
            test_dicts[sediment].w_2 = 0.00025

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.00006
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 3, 4],
                                                   [3, 9, 12],
                                                   [4, 12, 16]])

        elif sediment == TestSediments.COBBLE:

            test_dicts[sediment].name = 'Cobble'
            test_dicts[sediment].color = '#008B8B'

            test_dicts[sediment].a_rho = 2.5

            test_dicts[sediment].nu_p = 1.8
            test_dicts[sediment].delta_p = 0.01374

            test_dicts[sediment].nu_t = 1.01
            test_dicts[sediment].delta_t = 0.1

            test_dicts[sediment].gamma_2 = 3.0
            test_dicts[sediment].w_2 = 0.00025

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.00152
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 0, 0],
                                                   [0, 0, 0],
                                                   [0, 0, 0]])

        elif sediment == TestSediments.SANDY_GRAVEL:

            test_dicts[sediment].name = 'Sandy Gravel'
            test_dicts[sediment].color = '#BDB76B'

            test_dicts[sediment].a_rho = 2.492

            test_dicts[sediment].nu_p = 1.337
            test_dicts[sediment].delta_p = 0.01705

            test_dicts[sediment].nu_t = 0.156
            test_dicts[sediment].delta_t = 0.2

            test_dicts[sediment].gamma_2 = 3.0
            test_dicts[sediment].w_2 = 0.00018

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.000377
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 0, 0],
                                                   [0, 0, 0],
                                                   [0, 0, 0]])

        elif sediment == TestSediments.COARSE_SAND:

            test_dicts[sediment].name = 'Coarse Sand'
            test_dicts[sediment].color = '#FF8C00'

            test_dicts[sediment].a_rho = 2.231

            test_dicts[sediment].nu_p = 1.2503
            test_dicts[sediment].delta_p = 0.01638

            test_dicts[sediment].nu_t = 0.134
            test_dicts[sediment].delta_t = 0.075

            test_dicts[sediment].gamma_2 = 3.25
            test_dicts[sediment].w_2 = 0.00022

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.000362
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 0, 0],
                                                   [0, 0, 0],
                                                   [0, 0, 0]])

        elif sediment == TestSediments.MEDIUM_SAND:

            test_dicts[sediment].name = 'Medium Sand'
            test_dicts[sediment].color = '#FFD700'

            test_dicts[sediment].a_rho = 1.845

            test_dicts[sediment].nu_p = 1.1782
            test_dicts[sediment].delta_p = 0.01624

            test_dicts[sediment].nu_t = 0.002
            test_dicts[sediment].delta_t = 1.0

            test_dicts[sediment].gamma_2 = 3.25
            test_dicts[sediment].w_2 = 0.0001406

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.000359
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 0, 0],
                                                   [0, 0, 0],
                                                   [0, 0, 0]])

        elif sediment == TestSediments.FINE_SAND:

            test_dicts[sediment].name = 'Fine Sand'
            test_dicts[sediment].color = '#FFA07A'

            test_dicts[sediment].a_rho = 1.451

            test_dicts[sediment].nu_p = 1.1072
            test_dicts[sediment].delta_p = 0.01602

            test_dicts[sediment].nu_t = 0.002
            test_dicts[sediment].delta_t = 1.0

            test_dicts[sediment].gamma_2 = 3.25
            test_dicts[sediment].w_2 = 0.000086

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.000354
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 0, 0],
                                                   [0, 0, 0],
                                                   [0, 0, 0]])

        elif sediment == TestSediments.SILT:

            test_dicts[sediment].name = 'Silt'
            test_dicts[sediment].color = '#7FFF00'

            test_dicts[sediment].a_rho = 1.149

            test_dicts[sediment].nu_p = 0.9873
            test_dicts[sediment].delta_p = 0.00386

            test_dicts[sediment].nu_t = 0.002
            test_dicts[sediment].delta_t = 1.0

            test_dicts[sediment].gamma_2 = 3.25
            test_dicts[sediment].w_2 = 0.0000164

            test_dicts[sediment].gamma_3 = 3.0
            test_dicts[sediment].w_3 = 0.00004269
            test_dicts[sediment].aspect = 1.0

            test_dicts[sediment].fluct = np.array([[1, 0, 0],
                                                   [0, 0, 0],
                                                   [0, 0, 0]])

    return test_dicts


test_params = make_test_params_dict()
