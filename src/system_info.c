#include "system_info.h"
#include <stdio.h>
#include <string.h>
#include <omp.h>

void get_system_info(SystemInfo *info) {
    memset(info, 0, sizeof(SystemInfo));

    FILE *fp = fopen("/proc/cpuinfo", "r");
    if (fp) {
        char line[512];
        int core_count = 0;
        while (fgets(line, sizeof(line), fp)) {
            if (strncmp(line, "model name", 10) == 0 && info->cpu_model[0] == '\0') {
                char *colon = strchr(line, ':');
                if (colon) {
                    colon++;
                    while (*colon == ' ') colon++;
                    size_t len = strlen(colon);
                    if (len > 0 && colon[len-1] == '\n') len--;
                    if (len >= sizeof(info->cpu_model)) len = sizeof(info->cpu_model) - 1;
                    strncpy(info->cpu_model, colon, len);
                    info->cpu_model[len] = '\0';
                }
            }
            if (strncmp(line, "processor", 9) == 0) {
                core_count++;
            }
        }
        info->cpu_threads = core_count;
        fclose(fp);
    }

    int physical_cores = 0;
    fp = popen("grep -c 'core id' /proc/cpuinfo 2>/dev/null", "r");
    if (fp) {
        fscanf(fp, "%d", &physical_cores);
        pclose(fp);
    }
    info->cpu_cores = physical_cores > 0 ? physical_cores : info->cpu_threads;

    fp = fopen("/proc/meminfo", "r");
    if (fp) {
        char line[256];
        while (fgets(line, sizeof(line), fp)) {
            if (strncmp(line, "MemTotal:", 9) == 0) {
                sscanf(line + 9, "%lld", &info->total_memory_kb);
                break;
            }
        }
        fclose(fp);
    }

    fp = popen("uname -r 2>/dev/null", "r");
    if (fp) {
        fgets(info->kernel_version, sizeof(info->kernel_version), fp);
        size_t len = strlen(info->kernel_version);
        if (len > 0 && info->kernel_version[len-1] == '\n') info->kernel_version[len-1] = '\0';
        pclose(fp);
    }

    info->omp_max_threads = omp_get_max_threads();

    snprintf(info->compiler_info, sizeof(info->compiler_info),
             "gcc %d.%d.%d with -O3 -fopenmp -lpthread",
             __GNUC__, __GNUC_MINOR__, __GNUC_PATCHLEVEL__);
}
