import os
import scipy.io
import unittest
import numpy as np

from hyo2.abc.lib.testing import Testing
from hyo2.openbst.lib.models.jackson2.model import Model
from hyo2.openbst.lib.models.jackson2.model_output import ModelOutput
from hyo2.openbst.lib.models.jackson2.model_plotter import ModelPlotter
from hyo2.openbst.lib.models.jackson2.dicts import TestSediments


class TestLibModelsJackson2(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testing = Testing(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                                                     os.pardir)))

    def test__init__(self):
        _ = Model()

    def test_run(self):
        m = Model()

        with self.assertRaises(RuntimeError):
            m.run()

        m.use_default_mdl_params()
        with self.assertRaises(RuntimeError):
            m.run()

        m.use_test_sed_params(TestSediments.COARSE_SAND)
        m.run()

    def test_plotter(self):
        m = Model()
        m.use_default_mdl_params()
        m.use_test_sed_params(TestSediments.COARSE_SAND)

        plotter = ModelPlotter(mdl=m)
        plotter.plot()

    def compare(self, use_300k: bool = False):
        root_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
        testing = Testing(root_folder=root_folder)
        input_folder = testing.input_data_folder()
        jackson2_folder = os.path.join(input_folder, "jackson2")
        if use_300k:
            folder_freq = os.path.join(jackson2_folder, "300k")
        else:
            folder_freq = os.path.join(jackson2_folder, "20k")

        for sediment in TestSediments:

            mdl = Model()
            mdl.use_test_sed_params(sediment)
            mdl.use_default_mdl_params()
            if use_300k:
                mdl.mdl_params.f = 300000
            mdl.run()

            mat_folder = os.path.join(folder_freq, str(sediment).split('.')[-1].lower())
            mat_files = Testing.files(mat_folder, ext='.mat')
            mat_out = ModelOutput()

            for mat_file in mat_files:

                if "theta_g" in mat_file:
                    mat_out.theta_g = scipy.io.loadmat(mat_file)['thetg'].flatten()
                    self.assertTrue(np.isclose(mat_out.theta_g, mdl.out.theta_g).all())

                elif "ss_tot" in mat_file:
                    mat_out.ss_tot = scipy.io.loadmat(mat_file)['sstot'].flatten()
                    self.assertTrue(np.isclose(mat_out.ss_tot, mdl.out.ss_tot).all())

                elif "ss_rough" in mat_file:
                    mat_out.ss_rough = scipy.io.loadmat(mat_file)['ssrough'].flatten()
                    self.assertTrue(np.isclose(mat_out.ss_rough, mdl.out.ss_rough).all())

                elif "ss_vol" in mat_file:
                    mat_out.ss_vol = scipy.io.loadmat(mat_file)['ssvol'].flatten()
                    self.assertTrue(np.isclose(mat_out.ss_vol, mdl.out.ss_vol).all())

                elif "ref_loss" in mat_file:
                    mat_out.ref_loss = scipy.io.loadmat(mat_file)['refloss'].flatten()
                    self.assertTrue(np.isclose(mat_out.ref_loss, mdl.out.ref_loss).all())

    def test_compare_20k(self):
        self.compare(use_300k=False)

    # def test_compare_300k(self):
    #     self.compare(use_300k=True)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibModelsJackson2))
    return s
