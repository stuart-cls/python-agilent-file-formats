import shutil
import tempfile
import unittest
from pathlib import Path

from numpy import float64, isnan

from agilent_format import agilentMosaic

DMT = Path(__file__).parent.parent.joinpath("datasets/5_mosaic_agg1024.dmt")


class TestMosaic(unittest.TestCase):

    def test_load_mosaic(self):
        ai = agilentMosaic(DMT, MAT=False)
        self.assertEqual(ai.filename, str(DMT))
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
        ai = agilentMosaic(DMT, MAT=True)
        # Confirm image orientation
        self.assertAlmostEqual(ai.data[7, 1, 1], 1.14792180)
        self.assertAlmostEqual(ai.data[7, 2, 2], 1.14063489)
        self.assertAlmostEqual(ai.data[6, 2, 3], 0.28298783)

    def test_load_mosaic_64(self):
        ai = agilentMosaic(DMT, MAT=False, dtype=float64)
        self.assertAlmostEqual(ai.data[1, 2, 3], 0.28298783)

    def test_load_mosaic_vis(self):
        ai = agilentMosaic(DMT, MAT=False)
        self.assertEqual(len(ai.vis), 2)
        self.assertDictEqual(ai.vis[0],
                             {'name': "IR Cutout",
                              'image_ref': Path(DMT).parent.joinpath("IrCutout.bmp"),
                              'pos_x': 0,
                              'pos_y': 0,
                              'img_size_x': 701.0,
                              'img_size_y': 1444.0,})
        self.assertDictEqual(ai.vis[1],
                             {'name': "Entire Image",
                              'image_ref': Path(DMT).parent.joinpath("VisMosaicCollectImages_Thumbnail.bmp"),
                              'pos_x': -204.400785854617,
                              'pos_y': -201.8752228163994,
                              'img_size_x': 1530.0,
                              'img_size_y': 1688.0,})

    def test_load_partial_mosaic(self):
        """Test a (synthetic) incomplete mosaic"""
        with tempfile.TemporaryDirectory() as dir_name:
            dest = Path(dir_name)
            dmt = Path(DMT)
            shutil.copyfile(dmt, dest.joinpath(dmt.name))
            dmd0 = dmt.parent.joinpath("5_Mosaic_agg1024_0000_0000.dmd")
            shutil.copyfile(dmd0, dest.joinpath(dmd0.name))
            dmd1 = dmt.parent.joinpath("5_Mosaic_agg1024_0000_0001.dmd")
            shutil.copyfile(dmd1, dest.joinpath(dmd1.name))
            dmd2 = "5_Mosaic_agg1024_0001_0000.dmd"
            shutil.copyfile(dmd0, dest.joinpath(dmd2))

            ai = agilentMosaic(Path(dir_name, dmt.name), MAT=False)
            # Confirm image orientation (completed data)
            self.assertAlmostEqual(ai.data[0, 1, 1], 1.14792180)
            self.assertAlmostEqual(ai.data[0, 2, 2], 1.14063489)
            self.assertAlmostEqual(ai.data[1, 2, 3], 0.28298783)
            # Confirm empty region (4th quadrant) is NaNs
            self.assertTrue(isnan(ai.data[0, 4, 5]))
