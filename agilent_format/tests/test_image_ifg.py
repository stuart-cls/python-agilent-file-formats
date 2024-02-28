import unittest

from agilent_format import agilentImageIFG, agilentImage


class TestImageIFG(unittest.TestCase):

    def shared_info(self, aifg):
        self.assertEqual(aifg.data.shape, (8, 8, 311))
        self.assertEqual(aifg.info['Npts'], 311)
        self.assertEqual(aifg.info['StartPt'], -68)
        self.assertEqual(aifg.info['PtSep'], float(0.00012659827227975054))
        self.assertEqual(aifg.info['Effective Laser Wavenumber'], 15798.0039)
        self.assertEqual(aifg.info['Resolution'], 32)
        self.assertEqual(aifg.info['Symmetry'], "ASYM")
        self.assertEqual(aifg.info['Under Sampling Ratio'], 4)
        self.assertEqual(aifg.info['PixelAggregationSize'], 16)

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

    def test_ifg_processed_wn(self):
        f = "agilent_format/datasets/background_agg256.seq"
        f_dat = "agilent_format/datasets/background_agg256.dat"
        aifg = agilentImageIFG(f, MAT=False)
        wn_ifg = aifg.info['wavenumbers']
        ai = agilentImage(f_dat, MAT=False)
        self.assertEqual(ai.info['wavenumbers'], wn_ifg)
