import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from agilent import agilentImage, agilentMosaic

ai = agilentImage("var/fpa_refl_vi.pb.seq", MAT=False)
print(ai.data.shape)
img = ai.data.sum(axis=2)
print(img.shape)
imgplot = plt.imshow(img, origin='lower')
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
print(img.shape)
imgplot = plt.imshow(img, origin='lower')
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
