//
//  Mandelbrot.metal
//  Mandelbrot
//
//  Created by asd on 20/04/2019.
//  Copyright © 2019 voicesync. All rights reserved.
//

#include <metal_stdlib>
using namespace metal;

#include "Mandel.h"

kernel void Mandelbrot( device color*pixels[[buffer(0)]], //  fixed coded func
                       const device range &rng[[buffer(1)]],    // range
                       const device uint &width[[buffer(2)]],   // width
                       const device uint &height[[buffer(3)]],  // height
                       const device uint &iters[[buffer(4)]],  // iters
                       
                       uint2 position [[thread_position_in_grid]] )
{
    class Mandelbrot mb(rng, width, height, iters);
    
    pixels[position.x + position.y * width] = mb.generateZ(position.x, position.y, 4);
}
