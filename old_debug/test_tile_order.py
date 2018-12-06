import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from agilent_format import agilentImage, agilentMosaic

filename = "/data/users/Kelly/557-S2_1hrTFP_PT/557-S2_1hrTFP_PT.dms"
MAT = False

am = agilentMosaic(filename, MAT=MAT)
print(am.data.shape)
img = am.data.sum(axis=2)
print(img.shape)
if MAT:
    imgplot = plt.imshow(img, origin='upper')
else:
    imgplot = plt.imshow(img, origin='lower')
plt.show()
