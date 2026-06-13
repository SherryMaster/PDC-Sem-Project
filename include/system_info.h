#ifndef SYSTEM_INFO_H
#define SYSTEM_INFO_H

typedef struct {
    char cpu_model[256];
    int cpu_cores;
    int cpu_threads;
    long long total_memory_kb;
    char kernel_version[128];
    char compiler_info[128];
    int omp_max_threads;
} SystemInfo;

void get_system_info(SystemInfo *info);

#endif
