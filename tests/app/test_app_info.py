import os
import unittest

from hyo2.openbst.app import app_info
from matplotlib.colors import ListedColormap


class TestAppInfo(unittest.TestCase):

    # the same as from LibInfo

    def test_app_name(self):
        self.assertGreater(len(app_info.app_name), 0)

    def test_app_version(self):
        self.assertEqual(len(app_info.app_version.split(".")), 3)

    def test_app_author(self):
        self.assertGreater(len(app_info.app_author), 0)

    def test_app_author_name(self):
        self.assertGreater(len(app_info.app_author_email), 0)
        self.assertTrue("@" in app_info.app_author_email)

    def test_app_license(self):
        self.assertGreater(len(app_info.app_license), 0)

    def test_app_license_url(self):
        self.assertGreater(len(app_info.app_license_url), 0)
        self.assertTrue("http" in app_info.app_latest_url)

    def test_app_path(self):
        self.assertGreater(len(app_info.app_path), 0)
        self.assertTrue(os.path.exists(app_info.app_path))

    def test_app_url(self):
        self.assertGreater(len(app_info.app_url), 0)
        self.assertTrue("http" in app_info.app_url)

    def test_app_manual_url(self):
        self.assertGreater(len(app_info.app_manual_url), 0)
        self.assertTrue("http" in app_info.app_manual_url)

    def test_support_email_license_url(self):
        self.assertGreater(len(app_info.app_support_email), 0)
        self.assertTrue("@" in app_info.app_support_email)

    def test_latest_url(self):
        self.assertGreater(len(app_info.app_latest_url), 0)
        self.assertTrue("http" in app_info.app_latest_url)

    # additional specific tests

    def test_app_media_path(self):
        self.assertGreater(len(app_info.app_media_path), 0)
        self.assertTrue(os.path.exists(app_info.app_media_path))

    def test_app_main_window_object_name(self):
        self.assertGreater(len(app_info.app_main_window_object_name), 0)

    def test_app_license_path(self):
        self.assertGreater(len(app_info.app_license_path), 0)
        self.assertTrue(os.path.exists(app_info.app_license_path))

    def test_app_icon_path(self):
        self.assertGreater(len(app_info.app_icon_path), 0)
        self.assertTrue(os.path.exists(app_info.app_icon_path))

    def test_app_tabs_icon_size(self):
        self.assertGreater(app_info.app_tabs_icon_size, 0)

    def test_app_toolbars_icon_size(self):
        self.assertGreater(app_info.app_toolbars_icon_size, 0)

    def test_app_button_height(self):
        self.assertGreater(app_info.app_button_height, 0)

    def test_plot_font_size(self):
        self.assertGreater(app_info.plot_font_size, 0)

    def test_plot_rc_context(self):
        self.assertTrue(type(app_info.plot_rc_context), dict)

    def test_plot_raster_cmap(self):
        self.assertTrue(type(app_info.plot_bathy_cmap), ListedColormap)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAppInfo))
    return s
