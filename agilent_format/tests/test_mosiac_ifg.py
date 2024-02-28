import unittest
from pathlib import Path

from numpy import float64

from agilent_format import agilentMosaicIFG

DMT = Path(__file__).parent.parent.joinpath("datasets/5_mosaic_agg1024.dmt")


class TestMosaicIFG(unittest.TestCase):

    def test_load_ifg_mosaic(self):
        aifg = agilentMosaicIFG(DMT, MAT=False)
        self.assertEqual(aifg.filename, str(DMT))
        # Check parameters
        assert aifg.data.shape == (8, 4, 311)
        assert aifg.info['Npts'] == 311
        assert aifg.info['StartPt'] == -68
        assert aifg.info['PtSep'] == float(0.00012659827227975054)
        assert aifg.info['Effective Laser Wavenumber'] == 15798.0039
        assert aifg.info['Resolution'] == 32
        assert aifg.info['Symmetry'] == "ASYM"
        assert aifg.info['Under Sampling Ratio'] == 4
        assert aifg.info['PixelAggregationSize'] == 32
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[5, 1, 0], 0.7116039)
        self.assertAlmostEqual(aifg.data[6, 2, 0], 0.48532167)

    def test_load_ifg_mosaic_MAT(self):
        aifg = agilentMosaicIFG(DMT, MAT=True)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[5, 1, 0], 0.52554786)
        self.assertAlmostEqual(aifg.data[6, 2, 0], 0.7433825)

    def test_load_ifg_mosaic_64(self):
        aifg = agilentMosaicIFG(DMT, MAT=False, dtype=float64)
        self.assertAlmostEqual(aifg.data[5, 1, 0], 0.7116039)
