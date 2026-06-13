#ifndef ANALYZER_H
#define ANALYZER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <dirent.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <pthread.h>
#include <omp.h>

#define MAX_PATH 1024
#define MAX_FILES 4096
#define SOBEL_KERNEL_SIZE 3

typedef struct {
    int width;
    int height;
    int max_val;
    unsigned char *pixels;
} PPMImage;

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

typedef struct {
    char cpu_model[256];
    int cpu_cores;
    int cpu_threads;
    long long total_memory_kb;
    char kernel_version[128];
    char compiler_info[128];
    int omp_max_threads;
} SystemInfo;

typedef struct {
    char mode_name[32];
    double time_ms;
    int frames;
    long long pixels;
    long long edge_pixels;
    int workers;
    double speedup;
} BenchmarkResult;

PPMImage *read_ppm(const char *filepath);
void write_ppm(const char *filepath, const PPMImage *img);
void free_ppm(PPMImage *img);
PPMImage *apply_sobel(const PPMImage *input);
double get_time_ms(struct timeval start, struct timeval end);
int get_ppm_files(const char *dirpath, char files[][MAX_PATH], int *count);
void get_system_info(SystemInfo *info);
void print_report_header(void);
void print_benchmark_result(const BenchmarkResult *result, int index);
void print_report_footer(const BenchmarkResult *results, int count, const SystemInfo *info);

#endif
