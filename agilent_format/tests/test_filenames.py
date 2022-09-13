import pathlib
import tempfile
import unittest

import agilent_format


class TestFilenames(unittest.TestCase):

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._temp_path = pathlib.Path(self._temp_dir.name)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def add_files_to_dir(self, filenames):
        p = self._temp_path
        for fn in filenames:
            p.joinpath(p, fn).touch()

    def test_dmt_DMD(self):
        filenames = ["ab9.dmt",
                     "AB9.bsp",
                     "AB9.dat",
                     "AB9.dms",
                     "AB9.seq",
                     "AB9_0000_0000.dmd",
                     "AB9_0000_0000.drd",
                     ]
        self.add_files_to_dir(filenames)
        dmt = self._temp_path.joinpath(filenames[0])
        self.assertEqual(agilent_format.base_data_path(dmt).name, "AB9")
        self.assertEqual(agilent_format.check_files(dmt, ['.dmt', '.dmd']).name, "AB9")

    def test_dmt_DMD2(self):
        filenames = ["ab9.dmt",
                     "ab9.bsp",
                     "AB9.dat",
                     "AB9.dms",
                     "AB9.seq",
                     "AB9_0000_0000.dmd",
                     "AB9_0000_0000.drd",
                     ]
        self.add_files_to_dir(filenames)
        dmt = self._temp_path.joinpath(filenames[0])
        self.assertEqual(agilent_format.base_data_path(dmt).name, "AB9")
        self.assertEqual(agilent_format.check_files(dmt, ['.dmt', '.dmd']).name, "AB9")

    def test_dmt_DRD(self):
        filenames = ["ab9.dmt",
                     "AB9.bsp",
                     "AB9.dat",
                     "AB9.dms",
                     "AB9.seq",
                     "AB9_0000_0000.dmd",
                     "AB9_0000_0000.drd",
                     ]
        self.add_files_to_dir(filenames)
        dmt = self._temp_path.joinpath(filenames[0])
        self.assertEqual(agilent_format.base_data_path(dmt).name, "AB9")
        self.assertEqual(agilent_format.check_files(dmt, ['.dmt', '.drd']).name, "AB9")

    def test_dmt_dmd(self):
        filenames = ["ab9.dmt",
                     "ab9.bsp",
                     "ab9.dat",
                     "ab9.dms",
                     "ab9.seq",
                     "ab9_0000_0000.dmd",
                     "ab9_0000_0000.drd",
                     ]
        self.add_files_to_dir(filenames)
        dmt = self._temp_path.joinpath(filenames[0])
        self.assertEqual(agilent_format.base_data_path(dmt).name, "ab9")
        self.assertEqual(agilent_format.check_files(dmt, ['.dmt', '.dmd']).name, "ab9")

    def test_dmt_drd(self):
        filenames = ["ab9.dmt",
                     "ab9.bsp",
                     "ab9.dat",
                     "ab9.dms",
                     "ab9.seq",
                     "ab9_0000_0000.dmd",
                     "ab9_0000_0000.drd",
                     ]
        self.add_files_to_dir(filenames)
        dmt = self._temp_path.joinpath(filenames[0])
        self.assertEqual(agilent_format.base_data_path(dmt).name, "ab9")
        self.assertEqual(agilent_format.check_files(dmt, ['.dmt', '.drd']).name, "ab9")

    def test_dmt_DMD_reprocessed(self):
        filenames = ["ab9.dmt",
                     "ab9.bsp",
                     "ab9.dat",
                     "ab9.dms",
                     "ab9.seq",
                     "AB9_0000_0000.dmd",
                     "AB9_0000_0000.drd",
                     ]
        self.add_files_to_dir(filenames)
        dmt = self._temp_path.joinpath(filenames[0])
        self.assertEqual(agilent_format.base_data_path(dmt).name, "AB9")
        self.assertEqual(agilent_format.check_files(dmt, ['.dmt', '.dmd']).name, "AB9")