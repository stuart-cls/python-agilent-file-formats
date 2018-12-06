import unittest

from agilent_format import agilent

class TestUtils(unittest.TestCase):

    def test_fpa_size(self):
        Npts = 100
        datasize = 64**2 * Npts + 255
        self.assertEqual(agilent._fpa_size(datasize, Npts), 64)

    def test_fpa_size_nonsquare(self):
        Npts = 100
        datasize = 64 * 32 * Npts + 255
        with self.assertRaises(ValueError):
            agilent._fpa_size(datasize, Npts)
