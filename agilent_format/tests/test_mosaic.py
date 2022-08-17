import unittest
from pathlib import Path

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

    def test_load_mosaic_vis(self):
        f = "agilent_format/datasets/5_mosaic_agg1024.dmt"
        ai = agilentMosaic(f, MAT=False)
        self.assertEqual(len(ai.vis), 2)
        self.assertDictEqual(ai.vis[0],
                             {'name': "IR Cutout",
                              'image_ref': Path(f).parent.joinpath("IrCutout.bmp"),
                              'pos_x': 0,
                              'pos_y': 0,
                              'img_size_x': 701.0,
                              'img_size_y': 1444.0,})
        self.assertDictEqual(ai.vis[1],
                             {'name': "Entire Image",
                              'image_ref': Path(f).parent.joinpath("VisMosaicCollectImages_Thumbnail.bmp"),
                              'pos_x': -204.400785854617,
                              'pos_y': -201.8752228163994,
                              'img_size_x': 1530.0,
                              'img_size_y': 1688.0,})
