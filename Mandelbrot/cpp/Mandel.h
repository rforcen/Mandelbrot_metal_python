//
//  Mandelbrot.hpp
//  Mandelbrot
//
//  Created by asd on 20/04/2019.
//  Copyright © 2019 voicesync. All rights reserved.
//

#ifndef Mandelbrot_hpp
#define Mandelbrot_hpp

#include <stdlib.h>
#include "complex.h"
#include "ColorScale.h"

typedef uint32_t color; // aa bb gg rr  32 bit color
typedef uint8_t byte;
typedef struct { float x,y,z,w; } float4;
typedef float4 range;

const int clRed=0xff, clBlue=0xff0000, maxColors=4096;

class Mandelbrot {
public:

    int width=0, height=0;
    int iter=150, power=2;
    float xstart = -1, ystart = -1, xend = 1, yend = 1;
    
    Mandelbrot() {}
    Mandelbrot(range range, int w, int h, int iter, int power) {
        setRange(range);
        setSize(w,h);
        setIter(iter);
        this->power=power;
    }
    
    inline complexf zformula(complexf Z) {
        return Z.pow((unsigned)power);
    }
    
    void setSize(int w, int h) { this->width=w; this->height=h; }
    void setIter(int iter) { this->iter=iter; }
    void setRange(float x0, float y0, float x1, float y1) {
        xstart=x0; ystart=y0; xend=x1; yend=y1;
    }
    void setRangeSize(range range, int w, int h) {
        xstart=range.x; ystart=range.y; xend=range.z; yend=range.w;
        width=w; height=h;
    }
    void setRange(range range) {
        xstart=range.x; ystart=range.y; xend=range.z; yend=range.w;
    }
    
    color generateZ(int x, int y, int C=4) { //  using complex
        float col=0;

        complexf Z, Zinc=complexf(xstart + ((xend - xstart) / width) * x,
                                  ystart + ((yend - ystart) / height) * y);
        
        bool inset = true;
        for (int k = 0; k < iter; k++) {
            Z = zformula(Z) + Zinc;
            
            if (Z.sqmag() > C) {
                inset = false;
                col = k;
                break;
            }
        }
        return 0xff000000 | ((inset) ? 0 : ColorScaleHSL(clBlue, clRed, 20. *col/iter) );
    }
};
#endif /* Mandelbrot_hpp */
