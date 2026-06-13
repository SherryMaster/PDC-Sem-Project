# Parallel Batch Frame Analyzer

A CLI-based batch image edge detector that applies Sobel convolution across directories of PPM frames — now with a full Python GUI wrapper.

It supports three modes:

| Mode | Flag | Description |
|------|------|-------------|
| 1 – Sequential | `--mode 1` | Single-threaded, processes frames one at a time |
| 2 – Parallel Pthreads | `--mode 2` | Spawns `--workers N` threads; each processes a chunk of frames |
| 3 – OpenMP | `--mode 3` | Uses `#pragma omp parallel for` with dynamic scheduling and reduction |

---

## Requirements

### CLI binary
- GCC with OpenMP support (`-fopenmp`): `gcc` >= 4.9
- POSIX-compliant OS (Linux, macOS)
- pthreads, math (`-lm`) libraries

### GUI
- Python 3.8 or newer
- `tkinter` (ships with CPython; on Debian/Ubuntu install `python3-tk`)

### Test frame generation
- Python 3 with no external dependencies (uses only `random`, `os`)

---

## Build

```bash
# Build the CLI binary
make

# Or build and immediately open the GUI
make gui
```

The compiled binary is written to `bin/frame_analyzer`.

---

## Running the CLI

```bash
# Mode 1 — Sequential
./bin/frame_analyzer --mode 1 --dir /path/to/frames

# Mode 2 — Parallel (pthreads), 8 worker threads
./bin/frame_analyzer --mode 2 --dir /path/to/frames --workers 8

# Mode 3 — OpenMP
./bin/frame_analyzer --mode 3 --dir /path/to/frames

# Benchmark — runs all 3 modes and prints a comparison report
./bin/frame_analyzer --benchmark --dir /path/to/frames --workers 4
```

### CLI Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--mode <1\|2\|3>` | Yes* | Execution mode (*not required with `--benchmark`) |
| `--dir <path>` | Yes | Directory containing P3 PPM image files |
| `--workers N` | No | Number of threads for Pthreads mode (default: 4) |
| `--benchmark` | No | Run all 3 modes and print a comparison table |

### Input / Output

- **Input:** P3 PPM files (ASCII format). Binary P6 PPM will fail.
- **Output:** Written to `<input_dir>_output/` (e.g. `test_frames_output/`). Each output file is named `edge_<original_name>.ppm`.

---

## Running the GUI

```bash
# After building:
make gui

# Or directly:
python3 gui.py
```

### GUI Features

**Scanner Tab**
- Browse for a directory or type a path directly.
- Choose a scan mode from the dropdown:
  - *Sequential Scan*
  - *Parallel Scan (Pthreads)* — reveals a **Workers** spinbox (1–64)
  - *Parallel Scan (OpenMP)*
- Press **START SCAN**. Results appear in a terminal-style output panel showing: mode, total time, frames processed, total pixels, edge pixels, and worker count.

**Scan History Tab**
- Every completed scan is automatically logged.
- A table records: run number, mode, workers, frames, total pixels, edge pixels, time (ms), and timestamp.
- History is session-scoped (resets when the app is closed).

**Benchmark Tab**
- Configure the directory and worker count, then press **RUN BENCHMARK**.
- Runs all 3 execution modes back-to-back and displays:
  - **System Specs** — CPU model, cores, memory, kernel, compiler, OpenMP threads
  - **Benchmark Results** — side-by-side comparison with speedup calculations
- Export results to `.txt` (plain text) or `.csv` (spreadsheet-ready).

---

## Generating Test Frames

```bash
# Generate 20 random 512x512 P3 PPM test frames
make generate
```

This creates 20 images in `test_frames/` with random geometric shapes (rectangles, circles, triangles, lines) on random backgrounds. Useful for consistent benchmarking across all three modes.

---

## Architecture

The C backend is split into focused modules:

| Module | Responsibility |
|--------|---------------|
| `ppm.c` | PPM file I/O: reading, writing, memory management, directory scanning |
| `sobel.c` | Sobel 3x3 edge detection: grayscale conversion, convolution kernel, magnitude calculation |
| `system_info.c` | Hardware introspection: CPU model/cores, memory, kernel version, compiler info |
| `report.c` | Benchmark output: formatted tables, speedup analysis, system info display |
| `analyzer.c` | Glue layer: CLI parsing, mode dispatch (sequential/pthreads/openmp), thread worker, `main()` |

## Notes

- All three modes call the same `process_single_frame()` function per image, so output is identical regardless of execution strategy.
- Edge pixel counts should match exactly across modes — a mismatch indicates a race condition bug.
- The Sobel filter uses standard luminance weights (0.299R + 0.587G + 0.114B) for grayscale conversion.
- Border pixels are set to black since they lack a full 3x3 neighborhood for convolution.
- The benchmark timer uses `gettimeofday()` for microsecond-precision timing.
- OpenMP thread count is determined by `omp_get_max_threads()` (typically equals CPU core count).
- Pthreads mode distributes frames evenly: `floor(N/workers)` or `ceil(N/workers)` per thread.
- The mutex in Pthreads mode is locked only once per thread (at the end), not per frame.
- Output directory is auto-created with `mkdir(..., 0755)` if it does not exist.
- Files are sorted alphabetically via `qsort()` before processing for deterministic ordering.

---

## Makefile Targets

```
make           Build all modules and link into bin/frame_analyzer (default)
make clean     Remove object files, binary, test frames, and output directory
make generate  Generate 20 P3 PPM test frames (512x512) in test_frames/
make benchmark Build + run all 3 modes with comparison report
make gui       Build + launch the Python GUI
```

---

## Project Structure

```
.
├── src/
│   ├── analyzer.c           # Main entry point: CLI parsing, mode orchestration, thread worker
│   ├── ppm.c                # PPM image I/O (read, write, free, directory listing)
│   ├── sobel.c              # Sobel 3x3 edge detection convolution
│   ├── system_info.c        # System info gathering (/proc/cpuinfo, /proc/meminfo)
│   └── report.c             # Benchmark report printing and timing utilities
├── include/
│   ├── analyzer.h           # Aggregator header: includes all below + FrameJob, ThreadArg
│   ├── ppm.h                # PPMImage struct and I/O declarations
│   ├── sobel.h              # apply_sobel declaration
│   ├── system_info.h        # SystemInfo struct and get_system_info
│   └── report.h             # BenchmarkResult struct and print functions
├── gui.py                   # Tkinter GUI with 3 tabs and cyberpunk theme
├── scripts/
│   └── generate_frames.py   # Test frame generator (random geometric shapes)
├── bin/
│   └── frame_analyzer       # Compiled C binary (after make)
├── test_frames/             # Generated input PPM files
├── test_frames_output/      # Edge-detected output (auto-created)
├── Makefile
└── README.md
```
