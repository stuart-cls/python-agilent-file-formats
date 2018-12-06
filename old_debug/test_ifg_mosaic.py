import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from agilent_format import agilentMosaicIFG

PLOTS = True
ATTRS = False

filename = ["var/2018-01-02 Small Test File/5_mosaic_noimage_agg1024/5_mosaic_agg1024.dmt"]

for f in filename:
    aifg = agilentMosaicIFG(f)
    print(aifg.data.shape)

    if PLOTS:
        img = aifg.data.sum(axis=2)
        print(img.shape)
        imgplot = plt.imshow(img, origin='lower')
        plt.show()
        plt.plot(range(0, aifg.data.shape[2]), aifg.data[0,0,:])
        plt.plot(range(0, aifg.data.shape[2]), aifg.data[2,2,:])
        plt.plot(range(0, aifg.data.shape[2]), aifg.data[0,3,:])
        plt.show()

    assert aifg.data.shape == (8, 4, 311)
    assert aifg.info['Npts'] == 311
    assert aifg.info['StartPt'] == -68
    assert aifg.info['PtSep'] == float(0.00012659827227975054)
    assert aifg.info['Rapid Stingray']['Effective Laser Wavenumber'] == "15798.0039"
    assert aifg.info['Rapid Stingray']['Resolution'] == "32"
    try:
        assert aifg.info['Rapid Stingray']['Symmetry'] == "ASYM"
    except KeyError:
        print("No \'Symmetry\' key in " + aifg.filename)
    try:
        assert aifg.info['Rapid Stingray']['Under Sampling Ratio'] == "4"
    except KeyError:
        print("No \'Under Sampling Ratio\' key in " + aifg.filename)
    assert aifg.info['PixelAggregationSize'] == 32


if ATTRS:
    for k,v in aifg.info.items():
        if k == "Rapid Stingray":
            for k, v, in v.items():
                print(k,v, type(v))
        else:
            print(k,v, type(v))