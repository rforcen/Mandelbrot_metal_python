//
//  Mandelbrot.metal
//  Mandelbrot
//
//  Created by asd on 20/04/2019.
//  Copyright © 2019 voicesync. All rights reserved.
//

#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

namespace p = boost::python;
namespace np = boost::python::numpy;

#include "Mandel.h"
#include "Thread.h"

// threaded mandelbrot generator
class MandelbrotThreaded : public Mandelbrot {
public:
    color*image;

    MandelbrotThreaded(range range, int w, int h, int iter, int power) : Mandelbrot(range, w, h, iter, power) {
        image=new color[w*h];
    }

    color* generate() {
        Thread(width * height).run([this](int ix){
            image[ix] = generateZ(ix / width, ix % width);
        });
        return image;
    }
};

static void initPython() {
     Py_Initialize(); // init boost & numpy boost
     np::initialize();
}

// generate a h x w x 4 -> np.uint8 numpy array w/ mandelbrot fractal using multithreaded
static np::ndarray mandelbrot(p::list l_range, int w, int h, int iters, int power) {
    initPython();

    range range; // copy l_range to range
    for (int i=0; i<4; i++) ((float*)&range)[i]=p::extract<float>(l_range[i]);

    MandelbrotThreaded mth(range, w, h, iters, power);

    return np::from_data(mth.generate(),     // data -> image
            np::dtype::get_builtin<byte>(),  // dtype -> byte
            p::make_tuple(h, w, 4),          // shape -> h x w x 4
            p::make_tuple(w*4, 4, 1), p::object());    // stride in bytes [1,1,1,1] (4) each row = w x 4

}

BOOST_PYTHON_MODULE(Mandelbrot) {
    def("mandelbrot", mandelbrot, (p::arg("range"), p::arg("w"), p::arg("h"), p::arg("iters"), p::arg("power")));
}
