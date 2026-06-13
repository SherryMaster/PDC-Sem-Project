#ifndef PPM_H
#define PPM_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

#define MAX_PATH 1024
#define MAX_FILES 4096

typedef struct {
    int width;
    int height;
    int max_val;
    unsigned char *pixels;
} PPMImage;

PPMImage *read_ppm(const char *filepath);
void write_ppm(const char *filepath, const PPMImage *img);
void free_ppm(PPMImage *img);
int get_ppm_files(const char *dirpath, char files[][MAX_PATH], int *count);

#endif
