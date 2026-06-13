#include "report.h"
#include <stdio.h>
#include <string.h>

double get_time_ms(struct timeval start, struct timeval end) {
    return (double)(end.tv_sec - start.tv_sec) * 1000.0 +
           (double)(end.tv_usec - start.tv_usec) / 1000.0;
}

void print_report_header(void) {
    SystemInfo info;
    get_system_info(&info);

    printf("==================================================================\n");
    printf("         PARALLEL BATCH FRAME ANALYZER - BENCHMARK REPORT        \n");
    printf("==================================================================\n");
    printf("\n--- SYSTEM INFORMATION ---\n");
    printf("CPU Model       : %s\n", info.cpu_model[0] ? info.cpu_model : "Unknown");
    printf("Physical Cores  : %d\n", info.cpu_cores);
    printf("Logical Threads : %d\n", info.cpu_threads);
    printf("Total Memory    : %.1f GB\n", info.total_memory_kb / 1048576.0);
    printf("Kernel Version  : %s\n", info.kernel_version[0] ? info.kernel_version : "Unknown");
    printf("Compiler        : %s\n", info.compiler_info);
    printf("OpenMP Threads  : %d\n", info.omp_max_threads);
    printf("\n");
}

void print_benchmark_result(const BenchmarkResult *result, int index) {
    printf("--- Run %d: %s ---\n", index + 1, result->mode_name);
    printf("  Execution Time   : %.2f ms\n", result->time_ms);
    printf("  Frames Processed : %d\n", result->frames);
    printf("  Total Pixels     : %lld\n", result->pixels);
    printf("  Edge Pixels Found: %lld\n", result->edge_pixels);
    printf("  Workers Used     : %d\n", result->workers);
    printf("  Speedup vs Seq   : %.2fx\n", result->speedup);
    printf("\n");
}

void print_report_footer(const BenchmarkResult *results, int count, const SystemInfo *info) {
    (void)info;
    printf("==================================================================\n");
    printf("                        COMPARISON SUMMARY                        \n");
    printf("==================================================================\n");
    printf("%-14s | %12s | %8s | %10s | %8s\n",
           "Mode", "Time (ms)", "Workers", "Edge Pixels", "Speedup");
    printf("-----------------+--------------+----------+--------------+----------\n");

    for (int i = 0; i < count; i++) {
        printf("%-14s | %12.2f | %8d | %10lld | %7.2fx\n",
               results[i].mode_name,
               results[i].time_ms,
               results[i].workers,
               results[i].edge_pixels,
               results[i].speedup);
    }

    printf("\n--- ANALYSIS ---\n");
    if (count >= 2) {
        double seq = results[0].time_ms;
        for (int i = 1; i < count; i++) {
            double saved = seq - results[i].time_ms;
            double pct = (saved / seq) * 100.0;
            printf("  %s is %.2fx faster than Sequential (%.1f ms saved, %.1f%% improvement)\n",
                   results[i].mode_name, results[i].speedup, saved, pct);
        }
    }

    printf("\n--- WORKLOAD ---\n");
    if (count > 0) {
        printf("  Frames    : %d\n", results[0].frames);
        printf("  Pixels    : %lld per frame\n",
               results[0].frames > 0 ? results[0].pixels / results[0].frames : 0);
        printf("  Algorithm : Sobel 3x3 Edge Detection Convolution\n");
    }

    printf("\n==================================================================\n");
    printf("                        END OF REPORT                             \n");
    printf("==================================================================\n");
}
