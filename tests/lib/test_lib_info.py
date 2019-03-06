import os
import unittest

from hyo2.openbst.lib import lib_info


class TestLibInfo(unittest.TestCase):

    def test_lib_name(self):
        self.assertGreater(len(lib_info.lib_name), 0)

    def test_lib_version(self):
        self.assertEqual(len(lib_info.lib_version.split(".")), 3)

    def test_lib_author(self):
        self.assertGreater(len(lib_info.lib_author), 0)

    def test_lib_author_name(self):
        self.assertGreater(len(lib_info.lib_author_email), 0)
        self.assertTrue("@" in lib_info.lib_author_email)

    def test_lib_license(self):
        self.assertGreater(len(lib_info.lib_license), 0)

    def test_lib_license_url(self):
        self.assertGreater(len(lib_info.lib_license_url), 0)
        self.assertTrue("http" in lib_info.lib_latest_url)

    def test_lib_path(self):
        self.assertGreater(len(lib_info.lib_path), 0)
        self.assertTrue(os.path.exists(lib_info.lib_path))

    def test_lib_url(self):
        self.assertGreater(len(lib_info.lib_url), 0)
        self.assertTrue("http" in lib_info.lib_url)

    def test_lib_manual_url(self):
        self.assertGreater(len(lib_info.lib_manual_url), 0)
        self.assertTrue("http" in lib_info.lib_manual_url)

    def test_support_email_license_url(self):
        self.assertGreater(len(lib_info.lib_support_email), 0)
        self.assertTrue("@" in lib_info.lib_support_email)

    def test_latest_url(self):
        self.assertGreater(len(lib_info.lib_latest_url), 0)
        self.assertTrue("http" in lib_info.lib_latest_url)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibInfo))
    return s
