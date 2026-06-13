#include "sobel.h"

static int sobel_gx[3][3] = {
    {-1, 0, 1},
    {-2, 0, 2},
    {-1, 0, 1}
};

static int sobel_gy[3][3] = {
    {-1, -2, -1},
    { 0,  0,  0},
    { 1,  2,  1}
};

static unsigned char to_grayscale(unsigned char r, unsigned char g, unsigned char b) {
    return (unsigned char)(0.299 * r + 0.587 * g + 0.114 * b);
}

PPMImage *apply_sobel(const PPMImage *input) {
    PPMImage *output = (PPMImage *)malloc(sizeof(PPMImage));
    if (!output) return NULL;

    output->width = input->width;
    output->height = input->height;
    output->max_val = input->max_val;
    output->pixels = (unsigned char *)malloc(input->width * input->height * 3);
    if (!output->pixels) {
        free(output);
        return NULL;
    }

    int w = input->width;
    int h = input->height;

    unsigned char *gray = (unsigned char *)malloc(w * h);
    if (!gray) {
        free_ppm(output);
        return NULL;
    }

    for (int i = 0; i < w * h; i++) {
        gray[i] = to_grayscale(
            input->pixels[i * 3],
            input->pixels[i * 3 + 1],
            input->pixels[i * 3 + 2]
        );
    }

    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            if (x == 0 || x == w - 1 || y == 0 || y == h - 1) {
                int idx = (y * w + x) * 3;
                output->pixels[idx] = 0;
                output->pixels[idx + 1] = 0;
                output->pixels[idx + 2] = 0;
                continue;
            }

            int gx = 0;
            int gy = 0;
            for (int ky = -1; ky <= 1; ky++) {
                for (int kx = -1; kx <= 1; kx++) {
                    unsigned char pixel = gray[(y + ky) * w + (x + kx)];
                    gx += pixel * sobel_gx[ky + 1][kx + 1];
                    gy += pixel * sobel_gy[ky + 1][kx + 1];
                }
            }

            int magnitude = (int)sqrt((double)(gx * gx + gy * gy));
            if (magnitude > 255) magnitude = 255;

            int idx = (y * w + x) * 3;
            output->pixels[idx] = (unsigned char)magnitude;
            output->pixels[idx + 1] = (unsigned char)magnitude;
            output->pixels[idx + 2] = (unsigned char)magnitude;
        }
    }

    free(gray);
    return output;
}
