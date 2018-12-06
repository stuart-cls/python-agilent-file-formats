import struct

from agilent_format import _get_params

filename = "var/2017-11-10 4X-25X/2017-11-10 4x-25x.dmt"
#filename = "var/2017-11-10 4X-25X/2017-11-10 4x-25x.bsp"
#filename = "var/2018-01-02 Small Test File/4_noimage_agg256.bsp"
#filename = "var/2018-01-02 Small Test File/background_agg256.bsp"
#filename = "var/2018-01-02 Small Test File/background_agg1024.bsp"
filename = "C:\\Users\\reads\\tmp\\aff-testdata\\2017-11-24 USAF after FPA pumpdown\\USAF 25X Mosaic\\usaf 25x mosaic.bsp"

with open(filename, 'rb') as f:
    d = _get_params(f)

for k, v in d.items():
    try:
        for k2, v2 in v.items():
            print("{0} : {1}".format(k2, v2))
    except AttributeError:
        print("{0} : {1}".format(k, v))
