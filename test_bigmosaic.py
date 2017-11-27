import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from agilent import agilentImage, agilentMosaic

BIGMOSAIC = True

ai = agilentImage("var/fpa_refl_vi.pb.seq", MAT=True)
print(ai.data.shape)
img = ai.data.sum(axis=2)
print(img.shape)
imgplot = plt.imshow(img)
plt.show()

am = agilentMosaic("var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms", MAT=True)
print(am.data.shape)
img = am.data.sum(axis=2)
print(img.shape)
imgplot = plt.imshow(img)
plt.show()

am = agilentMosaic("var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms", MAT=False)
print(am.data.shape)
img = np.flipud(am.data.sum(axis=2))
print(img.shape)
imgplot = plt.imshow(img)
plt.show()

if BIGMOSAIC:
    am = agilentMosaic("/data/staff/reads/USAF 25X Mosaic/USAF 25X Mosaic.dms", MAT=True)
    print(am.data.shape)
    img = am.data.sum(axis=2)
    print(img.shape)
    imgplot = plt.imshow(img)
    plt.show()

    am = agilentMosaic("/data/staff/reads/USAF 25X Mosaic/USAF 25X Mosaic.dms", MAT=False)
    print(am.data.shape)
    img = np.flipud(am.data.sum(axis=2))
    print(img.shape)
    imgplot = plt.imshow(img)
    plt.show()
