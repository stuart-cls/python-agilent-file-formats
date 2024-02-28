import unittest
from pathlib import Path

from agilent_format import agilentImage

DAT = Path(__file__).parent.parent.joinpath("datasets/4_noimage_agg256.dat")

class TestImage(unittest.TestCase):

    def test_load_image(self):
        ai = agilentImage(DAT, MAT=False)
        # Check parameters
        Npts = ai.info['Npts']
        self.assertEqual(Npts, 9)
        self.assertEqual(Npts, len(ai.wavenumbers))
        self.assertEqual(ai.wavenumbers[0], ai.info['StartPt'] * ai.info['PtSep'])
        self.assertEqual(ai.wavenumbers[-1],
                         (ai.info['StartPt'] + Npts - 1) * ai.info['PtSep'])
        self.assertEqual(ai.data.shape, (8, 8, Npts))
        self.assertEqual(ai.info['FPA Pixel Size'], 5.5)
        self.assertEqual(ai.info['PixelAggregationSize'], 16)
        self.assertEqual(ai.width, ai.data.shape[0])
        self.assertEqual(ai.height, ai.data.shape[1])
        f_bsp = str(DAT.with_suffix(".bsp"))
        self.assertEqual(ai.filename, f_bsp)
        self.assertEqual(ai.acqdate, "Tuesday, January 02, 2018 14:01:52")
        # Confirm image orientation
        self.assertAlmostEqual(ai.data[0, 1, 1], 1.27181053)
        self.assertAlmostEqual(ai.data[0, 2, 2], 1.27506005)
        self.assertAlmostEqual(ai.data[1, 2, 3], 0.30882764)

    def test_load_image_MAT(self):
        ai = agilentImage(DAT, MAT=True)
        # Confirm image orientation
        self.assertAlmostEqual(ai.data[7, 1, 1], 1.27181053)
        self.assertAlmostEqual(ai.data[7, 2, 2], 1.27506005)
        self.assertAlmostEqual(ai.data[6, 2, 3], 0.30882764)