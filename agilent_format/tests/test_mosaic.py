import unittest

from numpy import float64

from agilent_format import agilentMosaic

class TestMosaic(unittest.TestCase):

    def test_load_mosaic(self):
        f = "agilent_format/datasets/5_mosaic_agg1024.dmt"
        ai = agilentMosaic(f, MAT=False)
        # Check parameters
        Npts = ai.info['Npts']
        self.assertEqual(Npts, 9)
        self.assertEqual(Npts, len(ai.wavenumbers))
        self.assertEqual(ai.wavenumbers[0], ai.info['StartPt'] * ai.info['PtSep'])
        self.assertEqual(ai.wavenumbers[-1],
                         (ai.info['StartPt'] + Npts - 1) * ai.info['PtSep'])
        self.assertEqual(ai.data.shape, (8, 4, Npts))
        self.assertEqual(ai.info['FPA Pixel Size'], 5.5)
        self.assertEqual(ai.info['PixelAggregationSize'], 32)
        # Confirm image orientation
        self.assertAlmostEqual(ai.data[0, 1, 1], 1.14792180)
        self.assertAlmostEqual(ai.data[0, 2, 2], 1.14063489)
        self.assertAlmostEqual(ai.data[1, 2, 3], 0.28298783)

    def test_load_mosaic_MAT(self):
        f = "agilent_format/datasets/5_mosaic_agg1024.dmt"
        ai = agilentMosaic(f, MAT=True)
        # Confirm image orientation
        self.assertAlmostEqual(ai.data[7, 1, 1], 1.14792180)
        self.assertAlmostEqual(ai.data[7, 2, 2], 1.14063489)
        self.assertAlmostEqual(ai.data[6, 2, 3], 0.28298783)

    def test_load_mosaic_64(self):
        f = "agilent_format/datasets/5_mosaic_agg1024.dmt"
        ai = agilentMosaic(f, MAT=False, dtype=float64)
        self.assertAlmostEqual(ai.data[1, 2, 3], 0.28298783)
