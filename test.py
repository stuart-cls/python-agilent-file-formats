import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from agilent import agilentImage, agilentMosaic

ai = agilentImage("var/fpa_refl_vi.pb.seq")
print(ai.data.shape)
img = ai.data.sum(axis=2)
print(img.shape)
imgplot = plt.imshow(img)
plt.show()

am = agilentMosaic("var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms")
print(am.data.shape)
img = am.data.sum(axis=2)
print(img.shape)
imgplot = plt.imshow(img)
plt.show()
