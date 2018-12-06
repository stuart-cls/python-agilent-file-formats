import unittest

from agilent_format import agilentImageIFG

class TestImageIFG(unittest.TestCase):

    @staticmethod
    def shared_info(aifg):
        assert aifg.data.shape == (8, 8, 311)
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
        try:
            assert aifg.info['PixelAggregationSize'] == 16
        except KeyError:
            print("TODO No \'PixelAggregationSize\' key in " + aifg.filename)
        except AssertionError:
            print("TODO Incorrect \'PixelAggregationSize\' {0} in {1}".format(aifg.info['PixelAggregationSize'], aifg.filename))

    def test_load_ifg_sample(self):
        f = "agilent_format/datasets/4_noimage_agg256.seq"
        aifg = agilentImageIFG(f, MAT=False)
        self.shared_info(aifg)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[1, 1, 0], 0.64558595)
        self.assertAlmostEqual(aifg.data[2, 2, 0], 0.5792696)

    def test_load_ifg_sample_MAT(self):
        f = "agilent_format/datasets/4_noimage_agg256.seq"
        aifg = agilentImageIFG(f, MAT=True)
        self.shared_info(aifg)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[1, 1, 0], 0.39676425)
        self.assertAlmostEqual(aifg.data[2, 2, 0], 0.8491539)

    def test_load_ifg_ref(self):
        f = "agilent_format/datasets/background_agg256.seq"
        aifg = agilentImageIFG(f, MAT=False)
        self.shared_info(aifg)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[1, 1, 0], 0.97700727)
        self.assertAlmostEqual(aifg.data[2, 2, 0], 1.0310643)