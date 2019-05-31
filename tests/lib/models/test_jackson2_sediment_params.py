import os
import unittest

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.models.jackson2.sediment_params import SedimentParams
from hyo2.openbst.lib.models.jackson2.dicts import test_params
from hyo2.openbst.lib.models.jackson2.dicts import TestSediments


class TestLibModelsJackson2SedimentParams(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                                                     os.pardir)))
        cls.nr_sediments = 6

    def test__init__(self):
        _ = SedimentParams()

    def test_enum(self):
        sed_enum = TestSediments
        # noinspection PyTypeChecker
        self.assertGreater(len(TestSediments), self.nr_sediments)

    def test_dict(self):
        self.assertGreater(len(test_params), self.nr_sediments)

        for sed in TestSediments:
            self.assertGreater(len(test_params[sed].name), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibModelsJackson2SedimentParams))
    return s
