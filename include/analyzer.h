#ifndef ANALYZER_H
#define ANALYZER_H

#include "ppm.h"
#include "sobel.h"
#include "system_info.h"
#include "report.h"

#include <pthread.h>
#include <omp.h>

typedef struct {
    char filepath[MAX_PATH];
    PPMImage *image;
    PPMImage *output;
} FrameJob;

typedef struct {
    FrameJob *jobs;
    int start;
    int end;
    long long *total_edge_pixels;
    pthread_mutex_t *mutex;
    char output_dir[MAX_PATH];
} ThreadArg;

void *thread_worker(void *arg);

#endif
