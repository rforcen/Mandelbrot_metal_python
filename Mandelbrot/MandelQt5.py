# mandelbrot plot using apple metal kernel shader and pymetal (runmetal-master)
# Mandel.metallib is generated compiling provided .metal sources with the 'compile' script
# shader generates a 4 byte int RGBA pixel image
# requires: runmetal, numpy, matplotlib

from PyQt5.QtWidgets import QMainWindow, QLabel, QSizePolicy, QApplication, QDesktopWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

import numpy as np
import runmetal
import sys


class Mandelbrot():
    def __init__(self, w, h, iters, power):
        self.w, self.h, self.iters, self.power = w, h, iters, power
        self.init_metal()

    def init_metal(self):
        self.pm = runmetal.PyMetal()
        self.pm.opendevice()
        self.pm.openlibrary_compiled('metal/Mandel.metallib')

    def run_metal(self, pixelbuf, parameters):
        cqueue, cbuffer = self.pm.getqueue()

        self.pm.runThread(cbuffer=cbuffer, func=self.fn, buffers=parameters,
                          threads=({"width": self.w, "height": self.h, "depth": 1}))

        self.pm.enqueue_blit(cbuffer, pixelbuf)

        self.pm.start_process(cbuffer)
        self.pm.wait_process(cbuffer)

    def intBuffer(self, i):
        return self.pm.numpybuffer(np.array(i, dtype=np.int32))

    def floatBuffer(self, f):
        return self.pm.numpybuffer(np.array(f, dtype=np.float32))

    def generate(self, w, h):
        self.w, self.h = w, h
        multFact = 2

        sizeBytes = self.w * self.h * 4

        self.fn = self.pm.getfn("Mandelbrot")  # get metal func Mandelbrot

        # create mtl buffers (pixels(w*h*4), range(xstart, ystart, xend, yend) float32, w,h, iters
        pixelbuf = self.pm.emptybuffer(sizeBytes)
        rangebuf = self.floatBuffer([-2.5, -1.5, 1.5, 1.5])
        wbuf = self.intBuffer(self.w)
        hbuf = self.intBuffer(self.h)
        itersbuf = self.intBuffer(self.iters)
        powerbuf = self.intBuffer(self.power)

        self.run_metal(pixelbuf, [pixelbuf, rangebuf, wbuf, hbuf, itersbuf, powerbuf])

        msg = f'generated {self.w:} x {self.h:} = {self.w*self.h:,} pixels mandelbrot^{self.power:}'

        # reshape result from int32 (color) to RGBA (byte)
        return self.pm.buf2numpy(pixelbuf, dtype=np.uint8).reshape(self.h, self.w, 4)


class QtWindow(QMainWindow):

    def __init__(self, w, h):
        super().__init__()
        self.w, self.h = w, h
        self.needsUpdate = True
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, self.w, self.h)

        self.pxlbl = QLabel()

        self.setCentralWidget(self.pxlbl)
        self.center()
        self.show()

    def center(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def mousePressEvent(self, QMouseEvent):  # update on click
        self.mandelbrot.power += 1
        self.resizeEvent(None)
        self.update()

    def generate(self):
        pass

    def resizeEvent(self,
                    event):  # generating metal content on resize issues: Context leak detected, msgtracer returned -1
        g = self.geometry()
        self.w, self.h = g.width(), g.height()
        self.generate()

    def paintEvent(self, event):
        if self.needsUpdate:
            self.needsUpdate = False  # avoid animating
            self.pxlbl.setPixmap(self.pixmap)


class MandelbrotQtWindow(QtWindow):
    def __init__(self, w, h, iters):
        self.mandelbrot = Mandelbrot(w=w, h=h, iters=iters, power=2)
        super().__init__(w, h)

    def generate_pixmap(self):
        w, h = self.w, self.h

        qimage = QImage(self.mandelbrot.generate(w, h), w, h, QImage.Format_ARGB32)
        return QPixmap(qimage).scaled(w, h, Qt.KeepAspectRatio)

    def generate(self):
        self.setWindowTitle(f'Mandelbrot - METAL ({self.w:} x {self.h:}, power:{self.mandelbrot.power:})')
        self.pixmap = self.generate_pixmap()
        self.needsUpdate = True


def main():
    app = QApplication(sys.argv)
    _ = MandelbrotQtWindow(w=1024, h=768, iters=2000)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
