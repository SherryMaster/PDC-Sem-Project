#ifndef REPORT_H
#define REPORT_H

#include <sys/time.h>
#include "system_info.h"

typedef struct {
    char mode_name[32];
    double time_ms;
    int frames;
    long long pixels;
    long long edge_pixels;
    int workers;
    double speedup;
} BenchmarkResult;

double get_time_ms(struct timeval start, struct timeval end);
void print_report_header(void);
void print_benchmark_result(const BenchmarkResult *result, int index);
void print_report_footer(const BenchmarkResult *results, int count, const SystemInfo *info);

#endif
