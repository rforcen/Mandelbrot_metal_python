from Mandelbrot import mandelbrot
import matplotlib.pyplot as plt

mf = 1
img = mandelbrot(range=[-1.5, -1.5, 2.2, .8], w=1024 * mf, h=768 * mf, iters=800, power=5)

plt.imshow(img)
plt.show()
