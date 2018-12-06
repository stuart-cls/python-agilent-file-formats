import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from agilent_format import agilentImage, agilentMosaic

am = agilentMosaic("/data/staff/reads/USAF 25X Mosaic/USAF 25X Mosaic.dms", MAT=False)
print(am.data.shape)
img = am.data.sum(axis=2)
extent = [0, am.data.shape[1]*am.info['FPA Pixel Size'],
          0, am.data.shape[0]*am.info['FPA Pixel Size']]
print(img.shape, extent)
imgplot = plt.imshow(img, origin='lower', extent=extent)
plt.show()

am = agilentMosaic("/data/staff/reads/USAF 25X Mosaic/USAF 25X Mosaic.dms", MAT=True)
print(am.data.shape)
img_m = am.data.sum(axis=2)
print(img.shape)
if np.array_equal(img_m, np.flipud(img)):
    print("MAT=True == MAT=False")
else:
    imgplot = plt.imshow(img)
    plt.show()
