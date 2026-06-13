# AGENTS.md

## Quick Commands

```bash
make                  # Build C binary -> bin/frame_analyzer
make clean            # Remove binary + test frames + output
make generate         # Generate 20 P3 PPM test frames (512x512) in test_frames/
make benchmark        # Run all 3 modes and print comparison report
make gui              # Build + launch Tkinter GUI
```

## Architecture

C backend (`src/analyzer.c`) + Python Tkinter GUI (`gui.py`). The GUI calls the C binary via `subprocess.run` and parses its stdout.

**Execution modes:**
- `--mode 1` Sequential (single-threaded loop)
- `--mode 2` Pthreads (N worker threads, mutex-guarded edge counter)
- `--mode 3` OpenMP (`#pragma omp parallel for reduction`)
- `--benchmark` Runs all 3, prints system info + comparison table

**CLI:** `./bin/frame_analyzer --mode <1|2|3> --dir <path> [--workers N] [--benchmark]`

**GUI:** `gui.py` uses 3 tabs: Scanner (single run), Scan History (session log), Benchmark Report (all-3-modes comparison with export to .txt/.csv).

## Gotchas

- **Edge outputs go to `<dir>_output/`**, not the input directory. This is intentional to avoid polluting input frames on repeated runs.
- **Input must be P3 PPM (ASCII)**. Binary P6 PPM will fail. The test frame generator produces P3.
- **C binary is a hard prerequisite for GUI.** If `bin/frame_analyzer` is missing, `make` first.
- **GUI benchmark runs in a daemon thread** (`threading.Thread`). The mainloop stays responsive. Results are dispatched back via `root.after(0, ...)`.
- **GCC flags require `-fopenmp -lpthread -lm`** in that order. Missing any causes linker errors.

## File Map

| Path | Role |
|------|------|
| `src/analyzer.c` | All C logic: PPM I/O, Sobel convolution, 3 modes, benchmark, system info |
| `include/analyzer.h` | Structs (`PPMImage`, `ThreadArg`, `SystemInfo`, `BenchmarkResult`) and function declarations |
| `gui.py` | Tkinter app with `FrameAnalyzerApp` class, 3 tabs, threaded benchmark execution |
| `scripts/generate_frames.py` | Generates random geometric shapes as P3 PPM |
| `Makefile` | Build, clean, generate, benchmark, gui targets |
| `test_frames/` | Input directory (generated .ppm files) |
| `test_frames_output/` | Edge-detected output (auto-created) |
