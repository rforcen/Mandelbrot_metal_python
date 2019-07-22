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

static void initPython() {
        Py_Initialize(); // init boost & numpy boost
        np::initialize();
}

np::ndarray generate(float x0, float y0, float x1, float y1, int w, int h, int iters, int power) {
    initPython();

    range range={x0, y0, x1, y1};
    Mandelbrot m(range, w, h, iters, power);

    int sz=w*h;
    color *img=new color[sz];

    Thread(sz).run([&m, &img, w](int ix){
        img[ix] = m.generateZ(ix/w, ix%w);
    });

    return np::from_data(img,                // data -> image
            np::dtype::get_builtin<byte>(),  // dtype -> byte
            p::make_tuple(h, w, 4),          // shape -> h x w x 4
            p::make_tuple(w*4, 4, 1), p::object());    // stride in bytes [1,1,1,1] (4) each row = w x 4

}

BOOST_PYTHON_MODULE(Mandelbrot) {
    def("generate", generate);
}
