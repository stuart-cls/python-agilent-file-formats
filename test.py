import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from agilent import agilentImage, agilentMosaic

ai = agilentImage("var/fpa_refl_vi.pb.seq", MAT=False)
print(ai.data.shape)
img = ai.data.sum(axis=2)
extent = [0, ai.data.shape[1]*ai.info['FPA Pixel Size'],
          0, ai.data.shape[0]*ai.info['FPA Pixel Size']]
print(img.shape, extent)
imgplot = plt.imshow(img, origin='lower', extent=extent)
plt.show()

ai = agilentImage("var/fpa_refl_vi.pb.seq", MAT=True)
print(ai.data.shape)
img_m = ai.data.sum(axis=2)
print(img.shape)
if np.array_equal(img_m, np.flipud(img)):
    print("MAT=True == MAT=False")
else:
    imgplot = plt.imshow(img, origin='upper')
    plt.show()

am = agilentMosaic("var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms", MAT=False)
print(am.data.shape)
img = am.data.sum(axis=2)
extent = [0, am.data.shape[1]*am.info['FPA Pixel Size'],
          0, am.data.shape[0]*am.info['FPA Pixel Size']]
print(img.shape, extent)
imgplot = plt.imshow(img, origin='lower', extent=extent)
plt.show()

am = agilentMosaic("var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms", MAT=True)
print(am.data.shape)
img_m = am.data.sum(axis=2)
print(img.shape)
if np.array_equal(img_m, np.flipud(img)):
    print("MAT=True == MAT=False")
else:
    imgplot = plt.imshow(img, origin='upper')
    plt.show()
