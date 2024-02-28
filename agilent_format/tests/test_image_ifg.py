import unittest
from pathlib import Path

from agilent_format import agilentImageIFG, agilentImage

SEQ = Path(__file__).parent.parent.joinpath("datasets/4_noimage_agg256.seq")
SEQR = Path(__file__).parent.parent.joinpath("datasets/background_agg256.seq")
DAT = Path(__file__).parent.parent.joinpath("datasets/background_agg256.dat")

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
        aifg = agilentImageIFG(SEQ, MAT=False)
        self.shared_info(aifg)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[1, 1, 0], 0.64558595)
        self.assertAlmostEqual(aifg.data[2, 2, 0], 0.5792696)

    def test_load_ifg_sample_MAT(self):
        aifg = agilentImageIFG(SEQ, MAT=True)
        self.shared_info(aifg)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[1, 1, 0], 0.39676425)
        self.assertAlmostEqual(aifg.data[2, 2, 0], 0.8491539)

    def test_load_ifg_ref(self):
        aifg = agilentImageIFG(SEQR, MAT=False)
        self.shared_info(aifg)
        # Confirm image orientation
        self.assertAlmostEqual(aifg.data[1, 1, 0], 0.97700727)
        self.assertAlmostEqual(aifg.data[2, 2, 0], 1.0310643)

    def test_ifg_processed_wn(self):
        aifg = agilentImageIFG(SEQ, MAT=False)
        wn_ifg = aifg.info['wavenumbers']
        ai = agilentImage(DAT, MAT=False)
        self.assertEqual(ai.info['wavenumbers'], wn_ifg)
