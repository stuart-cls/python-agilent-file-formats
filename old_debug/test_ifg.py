import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from agilent_format import agilentImageIFG

PLOTS = False
ATTRS = False

filename = ["var/2018-01-02 Small Test File/4_noimage_agg256.bsp"]
filename += ["var/2018-01-02 Small Test File/background_agg256.bsp"]

for f in filename:
    aifg = agilentImageIFG(f)
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

    assert aifg.data.shape == (8, 8, 311)
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
    try:
        assert aifg.info['PixelAggregationSize'] == 16
    except KeyError:
        print("No \'PixelAggregationSize\' key in " + aifg.filename)
    except AssertionError:
        print("Incorrect \'PixelAggregationSize\' {0} in {1}".format(aifg.info['PixelAggregationSize'], aifg.filename))

if ATTRS:
    for k,v in aifg.info.items():
        if k == "Rapid Stingray":
            for k, v, in v.items():
                print(k,v, type(v))
        else:
            print(k,v, type(v))