#ifndef SOBEL_H
#define SOBEL_H

#include "ppm.h"
#include <math.h>

#define SOBEL_KERNEL_SIZE 3

PPMImage *apply_sobel(const PPMImage *input);

#endif
