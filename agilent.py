__version__ = "0.1"
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
    #TODO Some filenames are written all lower-case by ResPro: Handle this
    # .dmt for sure, done
    p = Path(filename)
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
        part = dat.partition(bytes(param, encoding='utf8'))
        val = part[2][:100].lstrip(STRP).split(b'\x00')[0].strip(STRP)
        return val.decode('utf8', errors='replace')

    d = {}
    f.seek(0)
    dat = f.read()

    d['Visible Pixel Size'] = _get_prop_d(dat, 'Visible Pixel Size')
    d['FPA Pixel Size'] = _get_prop_d(dat, 'FPA Pixel Size')
    d['Rapid Stingray'] = _get_section(dat, 'Rapid Stingray')
    d['Time Stamp'] = d['Rapid Stingray']['Time Stamp']
    try:
        d['PixelAggregationSize'] = int(_get_prop_str(dat, 'PixelAggregationSize'))
    except ValueError:
        pass

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
        filename (str): full path to .seq file
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
        p = _check_files(filename, [".seq", ".dat", ".bsp"])
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


class agilentMosaic(DataObject):
    """
    Extracts the spectra from an Agilent mosaic FPA image.

    Attributes beyond .info and .data are provided for consistency with MATLAB code

    Args:
        filename (str): full path to .dms file
        MAT (bool):     Output array using image coordinates (matplotlib/MATLAB)

    Attributes:
        info (dict):            Dictionary of acquisition information
        data (:obj:`ndarray`):  3-dimensional array (height x width x wavenumbers)
        wavenumbers (list):     Wavenumbers in order of .data array
        width (int):            Width of mosaic in pixels (rows)
        height (int):           Width of mosaic in pixels (columns)
        filename (str):         Full path to .dms file
        acqdate (str):          Date and time of acquisition

    Based on agilent-file-formats MATLAB code by Alex Henderson:
    https://bitbucket.org/AlexHenderson/agilent-file-formats
    """

    def __init__(self, filename, MAT=False):
        super().__init__()
        p = _check_files(filename, [".dms", ".dmt", ".drd", ".dmd"])
        self.MAT = MAT
        self._get_dmt_info(p)
        self._get_dmd(p)

        self.wavenumbers = self.info['wavenumbers']
        self.width = self.data.shape[0]
        self.height = self.data.shape[1]
        self.filename = p.with_suffix(".dms").as_posix()
        self.acqdate = self.info['Time Stamp']

    def _get_dmt_info(self, p_in):
        # .dmt is always lowercase
        p = p_in.parent.joinpath(p_in.with_suffix(".dmt").name.lower())
        with p.open(mode='rb') as f:
            self.info.update(_get_wavenumbers(f))
            self.info.update(_get_params(f))

    def _get_dmd(self, p_in):
        # Determine mosiac dimensions by counting .dmd files
        xtiles = sum(1 for _ in
                p_in.parent.glob(p_in.stem + "_[0-9][0-9][0-9][0-9]_0000.dmd"))
        ytiles = sum(1 for _ in
                p_in.parent.glob(p_in.stem + "_0000_[0-9][0-9][0-9][0-9].dmd"))
        # _0000_0000.dmd primary file
        p = p_in.parent.joinpath(p_in.stem + "_0000_0000.dmd")
        Npts = self.info['Npts']
        fpasize = _fpa_size(p.stat().st_size / 4, Npts)
        # Allocate array
        # (rows, columns, wavenumbers)
        data = np.zeros((ytiles*fpasize, xtiles*fpasize, Npts),
                        dtype=np.float32)

        if DEBUG:
            print("{0} x {1} tiles found".format(xtiles, ytiles))
            print("FPA size is {}".format(fpasize))
            print("Total dimensions are {0} x {1} or {2} spectra.".format(
                xtiles*fpasize, ytiles*fpasize, xtiles*ytiles*fpasize**2))
            print(data.shape)

        for y in range(ytiles):
            for x in range(xtiles):
                p_dmd = p_in.parent.joinpath(p_in.stem + "_{0:04d}_{1:04d}.dmd".format(x,y))
                with p_dmd.open(mode='rb') as f:
                    tile = np.fromfile(f, dtype=np.float32)
                tile = _reshape_tile(tile, (Npts, fpasize, fpasize))
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
