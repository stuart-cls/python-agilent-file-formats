import unittest

from agilent_format import agilentMosaicIFG

class TestMosaicIFG(unittest.TestCase):

    def test_load_ifg_mosaic(self):
        f = "agilent_format/datasets/5_mosaic_agg1024.dmt"
        aifg = agilentMosaicIFG(f, MAT=False)
        # Check parameters
        assert aifg.data.shape == (8, 4, 311)
        assert aifg.info['Npts'] == 311
        assert aifg.info['StartPt'] == -68
        assert aifg.info['PtSep'] == float(0.00012659827227975054)
        assert aifg.info['Rapid Stingray']['Effective Laser Wavenumber'] == "15798.0039"
        assert aifg.info['Rapid Stingray']['Resolution'] == "32"
        try:
            assert aifg.info['Rapid Stingray']['Symmetry'] == "ASYM"
        except KeyError:
            print("TODO No \'Symmetry\' key in " + aifg.filename)
        try:
            assert aifg.info['Rapid Stingray']['Under Sampling Ratio'] == "4"
        except KeyError:
            print("TODO No \'Under Sampling Ratio\' key in " + aifg.filename)
        assert aifg.info['PixelAggregationSize'] == 32
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[5, 1, 0], 0.7116039)
        self.assertAlmostEqual(aifg.data[6, 2, 0], 0.48532167)

    def test_load_ifg_mosaic_MAT(self):
        f = "agilent_format/datasets/5_mosaic_agg1024.dmt"
        aifg = agilentMosaicIFG(f, MAT=True)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[5, 1, 0], 0.52554786)
        self.assertAlmostEqual(aifg.data[6, 2, 0], 0.7433825)