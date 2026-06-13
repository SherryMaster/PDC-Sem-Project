#include "analyzer.h"

static void process_single_frame(const char *input_path, const char *output_dir, long long *edge_pixel_count) {
    PPMImage *img = read_ppm(input_path);
    if (!img) return;

    PPMImage *edge = apply_sobel(img);
    if (!edge) {
        free_ppm(img);
        return;
    }

    long long local_edges = 0;
    int total = edge->width * edge->height * 3;
    for (int i = 0; i < total; i++) {
        if (edge->pixels[i] > 128) {
            local_edges++;
        }
    }
    if (edge_pixel_count) {
        *edge_pixel_count = local_edges;
    }

    const char *basename = strrchr(input_path, '/');
    basename = basename ? basename + 1 : input_path;
    char outpath[MAX_PATH];
    snprintf(outpath, MAX_PATH, "%s/edge_%s", output_dir, basename);
    write_ppm(outpath, edge);

    free_ppm(img);
    free_ppm(edge);
}

void *thread_worker(void *arg) {
    ThreadArg *targ = (ThreadArg *)arg;
    long long local_edges = 0;
    for (int i = targ->start; i < targ->end; i++) {
        long long frame_edges = 0;
        process_single_frame(targ->jobs[i].filepath, targ->output_dir, &frame_edges);
        local_edges += frame_edges;
    }
    pthread_mutex_lock(targ->mutex);
    *(targ->total_edge_pixels) += local_edges;
    pthread_mutex_unlock(targ->mutex);
    return NULL;
}

static int compare_strings(const void *a, const void *b) {
    return strcmp((const char *)a, (const char *)b);
}

static BenchmarkResult run_single_mode(int mode, const char *dirpath, char files[][MAX_PATH],
                                        int file_count, int workers, const char *output_dir) {
    (void)dirpath;
    BenchmarkResult result;
    memset(&result, 0, sizeof(BenchmarkResult));

    if (mode == 1) strncpy(result.mode_name, "Sequential", sizeof(result.mode_name));
    else if (mode == 2) strncpy(result.mode_name, "Pthreads", sizeof(result.mode_name));
    else if (mode == 3) strncpy(result.mode_name, "OpenMP", sizeof(result.mode_name));

    result.frames = file_count;
    result.workers = (mode == 2) ? workers : omp_get_max_threads();

    FrameJob *jobs = (FrameJob *)malloc(sizeof(FrameJob) * file_count);
    for (int i = 0; i < file_count; i++) {
        strncpy(jobs[i].filepath, files[i], MAX_PATH - 1);
    }

    PPMImage *sample = read_ppm(jobs[0].filepath);
    if (sample) {
        result.pixels = (long long)file_count * sample->width * sample->height;
        free_ppm(sample);
    }

    struct timeval t_start, t_end;
    long long total_edges = 0;

    gettimeofday(&t_start, NULL);

    if (mode == 1) {
        for (int i = 0; i < file_count; i++) {
            long long frame_edges = 0;
            process_single_frame(jobs[i].filepath, output_dir, &frame_edges);
            total_edges += frame_edges;
        }
    } else if (mode == 2) {
        pthread_t *threads = (pthread_t *)malloc(sizeof(pthread_t) * workers);
        ThreadArg *args = (ThreadArg *)malloc(sizeof(ThreadArg) * workers);
        pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

        int base = file_count / workers;
        int remainder = file_count % workers;
        int offset = 0;

        for (int i = 0; i < workers; i++) {
            int count = base + (i < remainder ? 1 : 0);
            args[i].jobs = jobs;
            args[i].start = offset;
            args[i].end = offset + count;
            args[i].total_edge_pixels = &total_edges;
            args[i].mutex = &mutex;
            strncpy(args[i].output_dir, output_dir, MAX_PATH - 1);
            offset += count;
            pthread_create(&threads[i], NULL, thread_worker, &args[i]);
        }

        for (int i = 0; i < workers; i++) {
            pthread_join(threads[i], NULL);
        }

        pthread_mutex_destroy(&mutex);
        free(threads);
        free(args);
    } else if (mode == 3) {
        #pragma omp parallel for reduction(+:total_edges) schedule(dynamic)
        for (int i = 0; i < file_count; i++) {
            long long frame_edges = 0;
            process_single_frame(jobs[i].filepath, output_dir, &frame_edges);
            total_edges += frame_edges;
        }
    }

    gettimeofday(&t_end, NULL);

    result.time_ms = get_time_ms(t_start, t_end);
    result.edge_pixels = total_edges;
    free(jobs);
    return result;
}

int main(int argc, char *argv[]) {
    int mode = 0;
    char dirpath[MAX_PATH] = "";
    int workers = 4;
    int benchmark = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc) {
            mode = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--dir") == 0 && i + 1 < argc) {
            strncpy(dirpath, argv[++i], MAX_PATH - 1);
        } else if (strcmp(argv[i], "--workers") == 0 && i + 1 < argc) {
            workers = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--benchmark") == 0) {
            benchmark = 1;
        }
    }

    if (dirpath[0] == '\0') {
        fprintf(stderr, "Usage: %s --mode <1|2|3> --dir <path> [--workers <N>] [--benchmark]\n", argv[0]);
        return 1;
    }

    if (!benchmark && mode == 0) {
        fprintf(stderr, "Usage: %s --mode <1|2|3> --dir <path> [--workers <N>] [--benchmark]\n", argv[0]);
        return 1;
    }

    char files[MAX_FILES][MAX_PATH];
    int file_count = 0;
    if (get_ppm_files(dirpath, files, &file_count) != 0) {
        return 1;
    }

    if (file_count == 0) {
        fprintf(stderr, "ERROR: No .ppm files found in %s\n", dirpath);
        return 1;
    }

    qsort(files, file_count, MAX_PATH, compare_strings);

    char output_dir[MAX_PATH];
    snprintf(output_dir, MAX_PATH, "%s_output", dirpath);
    mkdir(output_dir, 0755);

    if (benchmark) {
        print_report_header();

        SystemInfo info;
        get_system_info(&info);

        BenchmarkResult results[3];
        int run_count = 0;

        fprintf(stderr, "Running Sequential...\n");
        results[run_count] = run_single_mode(1, dirpath, files, file_count, workers, output_dir);
        results[run_count].speedup = 1.0;
        print_benchmark_result(&results[run_count], run_count);
        run_count++;

        fprintf(stderr, "Running Pthreads (%d workers)...\n", workers);
        results[run_count] = run_single_mode(2, dirpath, files, file_count, workers, output_dir);
        results[run_count].speedup = results[0].time_ms / results[run_count].time_ms;
        print_benchmark_result(&results[run_count], run_count);
        run_count++;

        int omp_threads = omp_get_max_threads();
        fprintf(stderr, "Running OpenMP (%d threads)...\n", omp_threads);
        results[run_count] = run_single_mode(3, dirpath, files, file_count, workers, output_dir);
        results[run_count].speedup = results[0].time_ms / results[run_count].time_ms;
        print_benchmark_result(&results[run_count], run_count);
        run_count++;

        print_report_footer(results, run_count, &info);

        return 0;
    }

    struct timeval t_start, t_end;
    long long total_edges = 0;

    gettimeofday(&t_start, NULL);

    FrameJob *jobs = (FrameJob *)malloc(sizeof(FrameJob) * file_count);
    for (int i = 0; i < file_count; i++) {
        strncpy(jobs[i].filepath, files[i], MAX_PATH - 1);
    }

    if (mode == 1) {
        for (int i = 0; i < file_count; i++) {
            long long frame_edges = 0;
            process_single_frame(jobs[i].filepath, output_dir, &frame_edges);
            total_edges += frame_edges;
        }
    } else if (mode == 2) {
        pthread_t *threads = (pthread_t *)malloc(sizeof(pthread_t) * workers);
        ThreadArg *args = (ThreadArg *)malloc(sizeof(ThreadArg) * workers);
        pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

        int base = file_count / workers;
        int remainder = file_count % workers;
        int offset = 0;

        for (int i = 0; i < workers; i++) {
            int count = base + (i < remainder ? 1 : 0);
            args[i].jobs = jobs;
            args[i].start = offset;
            args[i].end = offset + count;
            args[i].total_edge_pixels = &total_edges;
            args[i].mutex = &mutex;
            strncpy(args[i].output_dir, output_dir, MAX_PATH - 1);
            offset += count;
            pthread_create(&threads[i], NULL, thread_worker, &args[i]);
        }

        for (int i = 0; i < workers; i++) {
            pthread_join(threads[i], NULL);
        }

        pthread_mutex_destroy(&mutex);
        free(threads);
        free(args);
    } else if (mode == 3) {
        #pragma omp parallel for reduction(+:total_edges) schedule(dynamic)
        for (int i = 0; i < file_count; i++) {
            long long frame_edges = 0;
            process_single_frame(jobs[i].filepath, output_dir, &frame_edges);
            total_edges += frame_edges;
        }
    } else {
        fprintf(stderr, "ERROR: Invalid mode %d. Use 1, 2, or 3.\n", mode);
        free(jobs);
        return 1;
    }

    gettimeofday(&t_end, NULL);

    double elapsed = get_time_ms(t_start, t_end);
    long long total_pixels = (long long)file_count;
    if (file_count > 0) {
        PPMImage *sample = read_ppm(jobs[0].filepath);
        if (sample) {
            total_pixels = (long long)file_count * sample->width * sample->height;
            free_ppm(sample);
        }
    }

    const char *mode_str = "Unknown";
    if (mode == 1) mode_str = "Sequential";
    else if (mode == 2) mode_str = "Pthreads";
    else if (mode == 3) mode_str = "OpenMP";

    printf("MODE: %s | TOTAL_TIME: %.2fms | FRAMES: %d | PIXELS: %lld | EDGE_PIXELS: %lld | WORKERS: %d\n",
           mode_str, elapsed, file_count, total_pixels, total_edges,
           (mode == 2) ? workers : omp_get_max_threads());

    free(jobs);
    return 0;
}
