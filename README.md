# python-agilent-file-formats
Python library for reading FT-IR imaging datasets created by Resolutions Pro on
Agilent Cary instruments with FPA area detectors.

Port of https://bitbucket.org/AlexHenderson/agilent-file-formats/ to Python

Developed for use in the [orange-spectroscopy](https://github.com/Quasars/orange-spectroscopy) add-in, which is part 
of the [Quasar](https://quasar.codes/) data analysis program.

## Installation

The package can be installed from [PyPI](https://pypi.org) as:

`pip install agilent-format`

## Usage

There are four primary classes for loading data, depending on the type:

| Class              | Data Type                  | Extension   |
|--------------------|----------------------------|-------------|
| `agilentImage`     | Single-tile FPA image      | .dat        |
| `agilentMosaic`    | Mosaic FPA image           | .dmt        |
| `agilentImageIFG`  | Single-tile interferograms | .seq        |
| `agilentMosaicIFG` | Mosaic interferograms      | .dmt        |

To use, load the corresponding data loader class with the appropriate filename:

```python
from agilent_format import agilentImage

ai = agilentImage("agilent_format/datasets/4_noimage_agg256.dat")

ai.data         # 3-dimensional numpy array (height x width x wavenumbers)
ai.wavenumbers  # list of wavenumbers in order of .data array
# Pixel size can be calculated by:
px_size = ai.info['FPA Pixel Size'] * ai.info['PixelAggregationSize']
```