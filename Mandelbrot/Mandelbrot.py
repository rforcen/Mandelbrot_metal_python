# mandelbrot plot using apple metal kernel shader and pymetal (runmetal-master)
# Mandel.metallib is generated compiling provided .metal sources with the 'compile' script
# shader generates a 4 byte int RGBA pixel image
# requires: runmetal, numpy, matplotlib

'''
    # add this method to pymetal

    def runThread(self, cbuffer, func, buffers, threads=None, label=None):
        desc = Metal.MTLComputePipelineDescriptor.new()
        if label is not None:
            desc.setLabel_(label)
        desc.setComputeFunction_(func)
        state = self.dev.newComputePipelineStateWithDescriptor_error_(
            desc, objc.NULL)
        encoder = cbuffer.computeCommandEncoder()
        encoder.setComputePipelineState_(state)
        bufmax = 0
        for i, buf in enumerate(buffers):
            encoder.setBuffer_offset_atIndex_(buf, 0, i)
            if bufmax < buf.length():
                bufmax = buf.length()

        # threads

        # number of thread per group
        w = state.threadExecutionWidth()
        h = max(1, int(state.maxTotalThreadsPerThreadgroup() / w))
        log.debug("w,h=%d,%d, bufmax=%d", w, h, bufmax)
        tpg = self.getmtlsize({"width": w, "height": h, "depth": 1})

        # number of thread per grig
        ntg = self.getmtlsize(threads)
        log.debug("threads: %s %s", ntg, tpg)

        encoder.dispatchThreads_threadsPerThreadgroup_(ntg, tpg)
        log.debug("encode(compute) %s", label)
        encoder.endEncoding()
'''
import numpy as np
from timeit import default_timer as timer
import runmetal
import matplotlib.pyplot as plt


def init_metal():
    pm = runmetal.PyMetal()
    pm.opendevice()
    pm.openlibrary_compiled('metal/Mandel.metallib')
    return pm


def run_metal(pm, fn, pixelbuf, w, h, parameters):
    cqueue, cbuffer = pm.getqueue()

    pm.runThread(cbuffer=cbuffer, func=fn, buffers=parameters,
                 threads=({"width": w, "height": h, "depth": 1}))

    pm.enqueue_blit(cbuffer, pixelbuf)

    pm.start_process(cbuffer)
    t = timer()
    pm.wait_process(cbuffer)
    return timer() - t


def intBuffer(pm, i):
    return pm.numpybuffer(np.array(i, dtype=np.int32))


def floatBuffer(pm, f):
    return pm.numpybuffer(np.array(f, dtype=np.float32))


multFact = 3
w, h, iters = 1920 * multFact, 1080 * multFact, 650

sizeBytes = w * h * 4

pm = init_metal()
fn = pm.getfn("Mandelbrot")  # compile metal func Mandelbrot

# create mtl buffers (pixels(w*h*4), range(xstart, ystart, xend, yend) float32, w,h, iters
pixelbuf = pm.emptybuffer(sizeBytes)
rangebuf = floatBuffer(pm, [-2.5, -1.5, 1.5, 1.5])
wbuf = intBuffer(pm, w)
hbuf = intBuffer(pm, h)
itersbuf = intBuffer(pm, iters)

tm = run_metal(pm, fn, pixelbuf, w, h, [pixelbuf, rangebuf, wbuf, hbuf, itersbuf])

# reshape result from int32 (color) to RGBA (byte)
pixels = pm.buf2numpy(pixelbuf, dtype=np.uint8).reshape(h, w, 4)
plt.imshow(pixels)
plt.show()
