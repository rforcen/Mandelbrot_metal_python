from Mandelbrot import generate
import matplotlib.pyplot as plt
import numpy as np

w, h = 1024, 768
img = generate(-1.5, -1.5, 2.2, .8, w, h, 600, 6).reshape(h, w, 4)
plt.imshow(img)
plt.show()
