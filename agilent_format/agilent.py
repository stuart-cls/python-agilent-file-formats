__version__ = "0.3.2"
from pathlib import Path
import struct

import numpy as np

DEBUG = False

def _check_files(filename, exts):
    """
    takes filename string and list of extensions, checks that they all exist and
    returns a Path
    """
    #TODO test whether IOError (deprecated) or OSError is better handled by Orange
    p = Path(filename)
    if p.suffix == ".dmt":
        for child in p.parent.iterdir():
            if child.suffix == ".dmt":
                continue
            elif child.stem.casefold() == p.stem.casefold():
                p = child
                break
            elif child.stem.casefold() == (p.stem + "_0000_0000").casefold():
                p = child.with_name(child.stem.split("_0000_0000")[0] + p.suffix)
                break
    for ext in exts:
        if ext == ".dmt":
            # Always lowercase
            ps = p.parent.joinpath(p.with_suffix(ext).name.lower())
        elif ext in [".drd", ".dmd"]:
            # Always has at least _0000_0000 tile
            ps = p.parent.joinpath(p.stem + "_0000_0000" + ext)
        else:
            ps = p.with_suffix(ext)
        if not ps.is_file():
            raise OSError('File "{}" was not found.'.format(ps))
    return p

def _readint(f):
    return struct.unpack("i", f.read(4))[0]

def _readdouble(f):
    return struct.unpack("d", f.read(8))[0]

def _get_wavenumbers(f):
    """
    takes an open file handle, grabs the startwavenumber, numberofpoints and step,
    calculates wavenumbers array and returns all in dict
    """
    d = {}
    f.seek(2228)
    d['StartPt'] = _readint(f)
    f.seek(2236)
    d['Npts'] = _readint(f)
    f.seek(2216)
    d['PtSep'] = _readdouble(f)
    d['wavenumbers'] = [d['PtSep'] * (d['StartPt'] + i) for i in range(d['Npts'])]

    if DEBUG:
        for k,v in d.items():
            if k == "wavenumbers":
                print(k, len(v), v[0], v[-1], type(v))
            else:
                print(k,v, type(v))
    return d

def _get_params(f):
    """
    Takes an open file handle and reads a preset selection of parameters
    returns in a dictionary
    """
    STRP = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16\x17\x18'

    def _get_section(dat, section):
        skip = [b'', b'\n', b'\"', b'\t', b',', b'\r',
                b'\x0b', b'\x0c', b'\x0e', b'\x0f', b'\x1a', b'\x1c']
        d = {}
        part = dat.partition(bytes(section, encoding='utf8'))
        dat = part[2].lstrip(STRP)
        try:
            n = dat[0]
        except IndexError:
            raise IndexError("Section not found")
        dat = dat[1:].split(b'\x00')
        i = 0
        for n in range(n):
            while dat[i].strip(STRP) in skip:
                i += 1
            k = dat[i].strip(STRP).decode('utf8', errors='replace')
            i += 1
            while dat[i].strip(STRP) in skip:
                i += 1
            if dat[i].strip(STRP) in [b'Data', b'PropType']:
                # Give up, maybe end of section
                return d
            else:
                v = dat[i].strip(STRP).decode('utf8', errors='replace')
                i += 1
            d[k] = v
        return d

    def _get_prop_d(dat, param):
        part = dat.partition(bytes(param, encoding='utf8'))
        val_b = part[2].partition(bytes("1.00", encoding='utf8'))[2]
        val = struct.unpack("d", val_b[12:20])[0]
        return val

    def _get_prop_str(dat, param):
        b_param = b'\x00' + bytes(param, encoding='utf8') + b'\x04'
        part = dat.partition(b_param)
        val = part[2][:100].lstrip(STRP + b'\n').split(b'\x00')[0].strip(STRP)
        return val.decode('utf8', errors='replace')

    d = {}
    f.seek(0)
    dat = f.read()

    d['Visible Pixel Size'] = _get_prop_d(dat, 'Visible Pixel Size')
    d['FPA Pixel Size'] = _get_prop_d(dat, 'FPA Pixel Size')
    d['Rapid Stingray'] = _get_section(dat, 'Rapid Stingray')
    d['Time Stamp'] = d['Rapid Stingray']['Time Stamp']

    k_int = ['PixelAggregationSize',
             'Resolution',
             'Under Sampling Ratio',
    ]
    for k in k_int:
        try:
            d[k] = int(_get_prop_str(dat, k))
        except ValueError:
            pass

    k_float = ['Effective Laser Wavenumber',
    ]
    for k in k_float:
        try:
            d[k] = float(_get_prop_str(dat, k))
        except ValueError as e:
            pass

    k_str = ['Symmetry',
    ]
    for k in k_str:
        d[k] = _get_prop_str(dat, k)

    return d

def _get_ifg_params(f):
    """
    Takes an open file handle and reads a preset selection of parameters
    returns in a dictionary
    """
    def _get_proptype_data(dat, param):
        part = dat.partition(bytes(param, encoding='utf8'))
        val_b = part[2].partition(bytes("1.00", encoding='utf8'))[2]
        PtSep = struct.unpack("d", val_b[12:20])[0]
        StartPt = struct.unpack("i", val_b[24:28])[0]
        Npts = struct.unpack("i", val_b[32:36])[0]
        return PtSep, StartPt, Npts

    d = {}
    f.seek(0)
    dat = f.read()

    d['PtSep'], d['StartPt'], d['Npts'] = _get_proptype_data(dat, 'Interferogram')

    if DEBUG:
        for k,v in d.items():
            print(k,v, type(v))
    return d


def _fpa_size(datasize, Npts):
    """
    Determine FPA size (255 block preamble, wavenumbers, sqrt)
    FPA is most likely 128 or 64 pixels square
    This also provides sanity check for wavelengths array

    Args:
        datasize (int): size of data (after reading as float32)
        Npts (int):     number of points in spectra
    """
    fpasize = datasize - 255
    fpasize /= Npts
    if fpasize not in [(2**n)**2 for n in range(1,8)]:
        raise ValueError("Unexpected FPA size: {}".format(fpasize))
    fpasize = int(np.sqrt(fpasize))
    return fpasize

def _reshape_tile(data, shape):
    """
    Reshape and transpose FPA tile data
    """
    # Reshape ndarray
    data = data[255:]
    # Using shape attribute to raise error if a copy is made of the array
    data.shape = shape
    # Transpose to standard [ rows, columns, wavelengths ]
    data = np.transpose(data, (1,2,0))
    return data


class DataObject(object):
    """
    Simple container of a data array and information about that array.
    Based on PyMca5.DataObject

    Attributes:
        info (dict):            Dictionary of acquisition information
        data (:obj:`ndarray`):  n-dimensional array of data
    """

    def __init__(self):
        self.info = {}
        self.data = np.array([])


class agilentImage(DataObject):
    """
    Extracts the spectra from an Agilent single tile FPA image.

    Attributes beyond .info and .data are provided for consistency with MATLAB code

    Args:
        filename (str): full path to .dat file
        MAT (bool):     Output array using image coordinates (matplotlib/MATLAB)

    Attributes:
        info (dict):            Dictionary of acquisition information
        data (:obj:`ndarray`):  3-dimensional array (height x width x wavenumbers)
        wavenumbers (list):     Wavenumbers in order of .data array
        width (int):            Width of image in pixels (rows)
        height (int):           Width of image in pixels (columns)
        filename (str):         Full path to .bsp file
        acqdate (str):          Date and time of acquisition

    Based on agilent-file-formats MATLAB code by Alex Henderson:
    https://bitbucket.org/AlexHenderson/agilent-file-formats
    """

    def __init__(self, filename, MAT=False):
        super().__init__()
        p = _check_files(filename, [".dat", ".bsp"])
        self.MAT = MAT
        self._get_bsp_info(p)
        self._get_dat(p)

        self.wavenumbers = self.info['wavenumbers']
        self.width = self.data.shape[0]
        self.height = self.data.shape[1]
        self.filename = p.with_suffix(".bsp").as_posix()
        self.acqdate = self.info['Time Stamp']

    def _get_bsp_info(self, p_in):
        p = p_in.with_suffix(".bsp")
        with p.open(mode='rb') as f:
            self.info.update(_get_wavenumbers(f))
            self.info.update(_get_params(f))

    def _get_dat(self, p_in):
        p = p_in.with_suffix(".dat")
        with p.open(mode='rb') as f:
            data = np.fromfile(f, dtype=np.float32)
        fpasize = _fpa_size(data.size, self.info['Npts'])
        data = _reshape_tile(data, (self.info['Npts'], fpasize, fpasize))

        if self.MAT:
            # Rotate and flip tile to match matplotlib/MATLAB image coordinates
            data = np.flipud(data)

        self.data = data

        if DEBUG:
            print("FPA Size is {}".format(fpasize))

class agilentMosaicTiles(DataObject):
    """
    UNSTABLE API

    This class provides an array of _get_dmd() closures to allow lazy tile-by-tile
    file loading by consumers.

    The API is not considered stable at this time, so if you are wish to load
    mosiac files with a stable interface, use agilentMosaic as in previous
    versions.
    """

    def __init__(self, filename, MAT=False):
        super().__init__()
        p = _check_files(filename, [".dmt", ".dmd"])
        self.MAT = MAT
        self._get_dmt_info(p)
        self._get_tiles(p)

        self.wavenumbers = self.info['wavenumbers']
        self.width = self.tiles.shape[0] * self.info['fpasize']
        self.height = self.tiles.shape[1] * self.info['fpasize']
        self.filename = p.with_suffix(".dmt").as_posix()
        self.acqdate = self.info['Time Stamp']

    def _get_dmt_info(self, p_in):
        # .dmt is always lowercase
        p = p_in.parent.joinpath(p_in.with_suffix(".dmt").name.lower())
        with p.open(mode='rb') as f:
            self.info.update(_get_wavenumbers(f))
            self.info.update(_get_params(f))

    def _get_tiles(self, p_in):
        # Determine mosiac dimensions by counting .dmd files
        xtiles = sum(1 for _ in
                p_in.parent.glob(p_in.stem + "_[0-9][0-9][0-9][0-9]_0000.dmd"))
        ytiles = sum(1 for _ in
                p_in.parent.glob(p_in.stem + "_0000_[0-9][0-9][0-9][0-9].dmd"))
        # _0000_0000.dmd primary file
        p = p_in.parent.joinpath(p_in.stem + "_0000_0000.dmd")
        Npts = self.info['Npts']
        fpasize = self.info['fpasize'] = _fpa_size(p.stat().st_size / 4, Npts)

        if DEBUG:
            print("{0} x {1} tiles found".format(xtiles, ytiles))
            print("FPA size is {}".format(fpasize))
            print("Total dimensions are {0} x {1} or {2} spectra.".format(
                xtiles*fpasize, ytiles*fpasize, xtiles*ytiles*fpasize**2))

        tiles = np.zeros((xtiles, ytiles), dtype=object)
        for (x, y) in np.ndindex(tiles.shape):
            p_dmd = p_in.parent.joinpath(p_in.stem + "_{0:04d}_{1:04d}.dmd".format(x,y))
            tiles[x, y] = self._get_dmd(p_dmd, Npts, fpasize)
        self.tiles = tiles

    @staticmethod
    def _get_dmd(p_dmd, Npts, fpasize):
        def _get_dmd_data(p_dmd=p_dmd):
            with p_dmd.open(mode='rb') as f:
                tile = np.fromfile(f, dtype=np.float32)
            tile = _reshape_tile(tile, (Npts, fpasize, fpasize))
            return tile
        return _get_dmd_data


class agilentMosaic(agilentMosaicTiles):
    """
    Extracts the spectra from an Agilent mosaic FPA image.

    Attributes beyond .info and .data are provided for consistency with MATLAB code

    Args:
        filename (str):   full path to .dmt file
        MAT (bool):       Output array using image coordinates (matplotlib/MATLAB)
        dtype (np.dtype): Set dtype of output array (float32 or float64)

    Attributes:
        info (dict):            Dictionary of acquisition information
        data (:obj:`ndarray`):  3-dimensional array (height x width x wavenumbers)
        wavenumbers (list):     Wavenumbers in order of .data array
        width (int):            Width of mosaic in pixels (rows)
        height (int):           Width of mosaic in pixels (columns)
        filename (str):         Full path to .dmt file
        acqdate (str):          Date and time of acquisition

    Based on agilent-file-formats MATLAB code by Alex Henderson:
    https://bitbucket.org/AlexHenderson/agilent-file-formats
    """

    def __init__(self, filename, MAT=False, dtype=np.float32):
        super().__init__(filename, MAT)
        self.dtype = dtype
        self._get_data()

    def _get_data(self):
        xtiles = self.tiles.shape[0]
        ytiles = self.tiles.shape[1]
        Npts = self.info['Npts']
        fpasize = self.info['fpasize']
        # Allocate array
        # (rows, columns, wavenumbers)
        data = np.zeros((ytiles*fpasize, xtiles*fpasize, Npts),
                        dtype=self.dtype)
        if DEBUG:
            print("self.tiles: ", self.tiles.shape)
            print("self.data: ", data.shape)

        for (x, y) in np.ndindex(self.tiles.shape):
            tile = self.tiles[x, y]()
            if self.MAT:
                # Rotate and flip tile to match matplotlib/MATLAB image coordinates
                tile = np.flipud(tile)
                data[y*fpasize:(y+1)*fpasize, x*fpasize:(x+1)*fpasize, :] = tile
            else:
                # Tile data is in normal cartesian coordinates
                # but tile numbering (000x_000y)
                # is left-to-right, top-to-bottom (image coordinates)
                data[(ytiles-y-1)*fpasize:(ytiles-y)*fpasize, (x)*fpasize:(x+1)*fpasize, :] = tile

        self.data = data


class agilentImageIFG(DataObject):
    """
    Extracts the interferograms from an Agilent single tile FPA image.

    Args:
        filename (str): full path to .seq file
        MAT (bool):     Output array using image coordinates (matplotlib/MATLAB)

    Attributes:
        info (dict):            Dictionary of acquisition information
        data (:obj:`ndarray`):  3-dimensional array (height x width x wavenumbers)
        filename (str):         Full path to .bsp file
    """

    def __init__(self, filename, MAT=False):
        super().__init__()
        p = _check_files(filename, [".seq", ".bsp"])
        self.MAT = MAT
        self._get_bsp_info(p)
        self._get_seq(p)

        self.filename = p.with_suffix(".bsp").as_posix()

    def _get_bsp_info(self, p_in):
        p = p_in.with_suffix(".bsp")
        with p.open(mode='rb') as f:
            self.info.update(_get_ifg_params(f))
            self.info.update(_get_params(f))

    def _get_seq(self, p_in):
        p = p_in.with_suffix(".seq")
        with p.open(mode='rb') as f:
            data = np.fromfile(f, dtype=np.float32)
        fpasize = _fpa_size(data.size, self.info['Npts'])
        data = _reshape_tile(data, (self.info['Npts'], fpasize, fpasize))

        if self.MAT:
            # Rotate and flip tile to match matplotlib/MATLAB image coordinates
            data = np.flipud(data)

        self.data = data

        if DEBUG:
            print("FPA Size is {}".format(fpasize))


class agilentMosaicIFGTiles(DataObject):
    """
    UNSTABLE API

    This class provides an array of _get_drd() closures to allow lazy tile-by-tile
    file loading by consumers.

    The API is not considered stable at this time, so if you are wish to load
    mosiac files with a stable interface, use agilentMosaic as in previous
    versions.
    """

    def __init__(self, filename, MAT=False):
        super().__init__()
        p = _check_files(filename, [".dmt", ".drd"])
        self.MAT = MAT
        self._get_dmt_info(p)
        self._get_tiles(p)

        self.filename = p.with_suffix(".dmt").as_posix()

    def _get_dmt_info(self, p_in):
        # .dmt is always lowercase
        p = p_in.parent.joinpath(p_in.with_suffix(".dmt").name.lower())
        with p.open(mode='rb') as f:
            self.info.update(_get_ifg_params(f))
            self.info.update(_get_params(f))

    def _get_tiles(self, p_in):
        # Determine mosiac dimensions by counting .drd files
        xtiles = sum(1 for _ in
                p_in.parent.glob(p_in.stem + "_[0-9][0-9][0-9][0-9]_0000.drd"))
        ytiles = sum(1 for _ in
                p_in.parent.glob(p_in.stem + "_0000_[0-9][0-9][0-9][0-9].drd"))
        # _0000_0000.drd primary file
        p = p_in.parent.joinpath(p_in.stem + "_0000_0000.drd")
        Npts = self.info['Npts']
        fpasize = self.info['fpasize'] = _fpa_size(p.stat().st_size / 4, Npts)

        if DEBUG:
            print("{0} x {1} tiles found".format(xtiles, ytiles))
            print("FPA size is {}".format(fpasize))
            print("Total dimensions are {0} x {1} or {2} spectra.".format(
                xtiles*fpasize, ytiles*fpasize, xtiles*ytiles*fpasize**2))

        tiles = np.zeros((xtiles, ytiles), dtype=object)
        for (x, y) in np.ndindex(tiles.shape):
            p_drd = p_in.parent.joinpath(p_in.stem + "_{0:04d}_{1:04d}.drd".format(x,y))
            tiles[x, y] = self._get_drd(p_drd, Npts, fpasize)
        self.tiles = tiles

    @staticmethod
    def _get_drd(p_drd, Npts, fpasize):
        def _get_drd_data(p_drd=p_drd):
            with p_drd.open(mode='rb') as f:
                tile = np.fromfile(f, dtype=np.float32)
            tile = _reshape_tile(tile, (Npts, fpasize, fpasize))
            return tile
        return _get_drd_data


class agilentMosaicIFG(agilentMosaicIFGTiles):
    """
    Extracts the interferograms from an Agilent mosaic FPA image.

    Args:
        filename (str):   full path to .dmt file
        MAT (bool):       Output array using image coordinates (matplotlib/MATLAB)
        dtype (np.dtype): Set dtype of output array (float32 or float64))

    Attributes:
        info (dict):            Dictionary of acquisition information
        data (:obj:`ndarray`):  3-dimensional array (height x width x wavenumbers)
        filename (str):         Full path to .dmt file
    """

    def __init__(self, filename, MAT=False, dtype=np.float32):
        super().__init__(filename, MAT)
        self.dtype = dtype
        self._get_data()

    def _get_data(self):
        xtiles = self.tiles.shape[0]
        ytiles = self.tiles.shape[1]
        Npts = self.info['Npts']
        fpasize = self.info['fpasize']
        # Allocate array
        # (rows, columns, wavenumbers)
        data = np.zeros((ytiles*fpasize, xtiles*fpasize, Npts),
                        dtype=self.dtype)
        if DEBUG:
            print("self.tiles: ", self.tiles.shape)
            print("self.data: ", data.shape)

        for (x, y) in np.ndindex(self.tiles.shape):
            tile = self.tiles[x, y]()
            if self.MAT:
                # Rotate and flip tile to match matplotlib/MATLAB image coordinates
                tile = np.flipud(tile)
                data[y*fpasize:(y+1)*fpasize, x*fpasize:(x+1)*fpasize, :] = tile
            else:
                # Tile data is in normal cartesian coordinates
                # but tile numbering (000x_000y)
                # is left-to-right, top-to-bottom (image coordinates)
                data[(ytiles-y-1)*fpasize:(ytiles-y)*fpasize, (x)*fpasize:(x+1)*fpasize, :] = tile

        self.data = data
