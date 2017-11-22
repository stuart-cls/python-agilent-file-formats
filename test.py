import matplotlib.pyplot as plt
import matplotlib.image as mpimg


from agilent import agilentImage

ai = agilentImage("var/fpa_refl_vi.pb.seq")
print(ai.data.shape)
img = ai.data.sum(axis=2)
print(img.shape)
imgplot = plt.imshow(img)
plt.show()
