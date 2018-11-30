import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from agilent import agilentImageIFG

PLOTS = True

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