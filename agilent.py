from pathlib import Path
import struct

import numpy as np

DEBUG = True

def _check_files(filename, exts):
    """
    takes filename string and list of extensions, checks that they all exist and
    returns a Path
    """
    #TODO test whether IOError (deprecated) or OSError is better handled by Orange
    #TODO I think some filenames are written all lower-case by ResPro: Handle this
    p = Path(filename)
    for ext in exts:
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

    pyrespro: #TODO
    dx = spec.Spectrum.PtSep
    startx = spec.Spectrum.StartPt
    N = spec.Spectrum.Npts
    xdata = [dx * (startx + i) for i in range(N)]
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

def _get_date(f):
    """
    takes an open file handle, grabs the date time string, converts to timestamp
    returns all in Dictionary
    #TODO actually return timestamp
    #TODO check date format matches MATLAB code?
    """
    d = {}
    #TODO Actually params section seems to start at 16000, time stamp (label) is at
    # 16435/16489 but that might be not always the case.
    # (MATLAB code just searches for Time Stamp plus a regexp of a timestamp)
    # Could be that 16000 is the known start of the params section and then you
    # read it in a logical way
    f.seek(16489)
    d['Time Stamp'] = f.read(46).partition(b'\x04')[0].decode()

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
    fpasize = int(np.sqrt(fpasize))
    if fpasize not in [32, 64, 128]:
        raise ValueError("Unexpected FPA size: {}".format(fpasize))
    return fpasize


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

    def __init__(self, filename):
        super().__init__()
        p = _check_files(filename, [".seq", ".dat", ".bsp"])
        self._get_bsp_info(p)
        self._get_dat(p)

    def _get_bsp_info(self, p_in):
        p = p_in.with_suffix(".bsp")
        with p.open(mode='rb') as f:
            self.info.update(_get_wavenumbers(f))
            self.info.update(_get_date(f))

    def _get_dat(self, p_in):
        p = p_in.with_suffix(".dat")
        with p.open(mode='rb') as f:
            data = np.fromfile(f, dtype=np.float32)
        fpasize = _fpa_size(data.size, self.info['Npts'])
        # Reshape ndarray
        data = data[255:]
        # Using shape attribute to raise error if a copy is made of the array
        data.shape = (self.info['Npts'], fpasize, fpasize)
        # Transpose to standard [ rows, columns, wavelengths ]
        data = np.transpose(data, (1,2,0))
        # Rotate and flip array
        data = np.rot90(data, 2)
        data = np.fliplr(data)
        # Return array
        self.data = data

        if DEBUG:
            print("FPA Size is {}".format(fpasize))
