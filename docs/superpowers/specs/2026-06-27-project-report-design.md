# Project Report Design — Parallel Batch Frame Analyzer

**Date:** 2026-06-27
**Topic:** Semester project report (DOCX) modeled on the UCP PDC sample template, populated for the Parallel Batch Frame Analyzer codebase.

## Goal

Produce a single `.docx` file (`/home/sherry/Documents/UCP/Sem 6/PDC/Lab/Project/report.docx`) that mirrors the structure, tone, and visual rhythm of the 14-page UCP PDC sample report — including its circular UCP seal on the cover — but is populated entirely with content drawn from the actual `frame_analyzer` codebase and live benchmark runs.

The report is a deliverable for a university semester project. It must be self-contained, accurate, and verifiable: every timing number, every code listing, and every system-specification value must trace back to either (a) the project's `src/` files, `gui.py`, or `Makefile`, or (b) a real execution of the project on the development machine.

## Constraints (decided with the user)

| # | Decision | Value |
|---|----------|-------|
| 1 | Cover page style | UCP-style cover, topic matches actual project |
| 2 | Cover fields | `Submitted by: Shaheer Ahmed, Reg: L1F23BSAI0005, Degree: BSAI` (no supervisor line — student has no supervisor) |
| 3 | Output format | DOCX only (`.docx`) |
| 4 | Module structure | 3 "modules" = 3 execution modes (Sequential, Pthread, OpenMP) |
| 5 | GUI section | Dedicated section after the 3 C-mode modules |
| 6 | MPI section replacement | Replaced with "Build & Execution" (System Specifications keeps its template position at section 6) |
| 7 | Code listings | Real `src/` code, trimmed to 30–50 lines per listing |
| 8 | Timing tables | One unified table (rows = mode, cols = workers 1/2/4/8) |
| 9 | References | 6–8 generic references (OpenMP, pthreads, Sobel, P3 PPM, Amdahl, Tkinter, Python) |
| 10 | Figures | 1–2 sample input/output PPM frames converted to PNG, plus the UCP circular-seal logo (downloaded) |
| 11 | Output path | Project root: `report.docx` |

## Architecture

The report is generated, not hand-authored. A single Python script (`scripts/build_report.py`) reads structured content and emits `report.docx` using `python-docx`.

```
                +-------------------------+
                |  report_content.json    |   <- prose, code excerpts, table data
                +----------+--------------+
                           |
                           v
                +-------------------------+
                |  sample_*.png figures   |   <- converted once from PPM
                +----------+--------------+
                           |
                           v
   +------------------- scripts/build_report.py -------------------+
   |  - load json                                                    |
   |  - apply docx styles (Title, Heading 1/2/3, Code, Body)         |
   |  - insert cover page                                            |
   |  - insert each section (heading + body)                         |
   |  - insert code listings (monospace, shaded background)          |
   |  - insert figures (centered, captioned)                         |
   |  - insert comparison table (grid borders)                       |
   |  - insert references (hanging indent)                           |
   +----------------------------+------------------------------------+
                                v
                       /.../Project/report.docx
```

### Components

| Path | Role |
|------|------|
| `scripts/build_report.py` | Generator script. Assembles the .docx from structured inputs. |
| `scripts/report_content.json` | All prose content, code listings, table data, references. Single source of truth. |
| `scripts/figures/make_figures.py` | One-shot PPM → PNG conversion using Pillow (PIL). |
| `scripts/figures/ucp_logo.jpg` | UCP circular seal downloaded from Wikipedia Commons (matches the sample's cover-page logo). |
| `scripts/figures/fetch_ucp_logo.sh` | Idempotent downloader. Skips if `ucp_logo.jpg` already present. |
| `report.docx` | Final output, written to project root. |

### UCP cover logo

The cover page needs a UCP seal. The sample template shows a circular seal with "University of Central Punjab, Lahore, Pakistan" around the edge and a stylized building/UCP monogram in the center. The same logo is available on Wikipedia Commons:

- **Source URL:** `https://upload.wikimedia.org/wikipedia/en/e/eb/University_of_Central_Punjab_%28logo%29.jpg`
- **Saved as:** `scripts/figures/ucp_logo.jpg` (≈11 KB, JPG)
- **Acquired via:** `scripts/figures/fetch_ucp_logo.sh` (one-line `curl -sL -o ...` with `if [ ! -f ... ]` guard for idempotency)
- **Used in report at:** cover page, centered, ~2 inches (≈ 5 cm) wide, with a 0.25-inch gap below before the "UNIVERSITY OF CENTRAL PUNJAB" title text

The script makes this fully reproducible: a fresh clone with no logo can fetch it in one command.

### Why a generator script (not manual Word editing)

- **Reproducible:** running the script twice with the same inputs produces identical output.
- **Auditable:** all content lives in plain text JSON — easy to diff, review, and amend.
- **No Word dependency:** the build can run on any machine with `python-docx` and `Pillow`; no Microsoft Word or ImageMagick required.
- **Logo fetcher is idempotent:** if `scripts/figures/ucp_logo.jpg` already exists, `fetch_ucp_logo.sh` skips the download. CI / repeated builds are safe.
- **Reusable:** the next semester report (different topic, same template) reuses the script with a different `report_content.json`.

## Document outline (11 numbered sections + cover, mirrors the sample template)

| # | Section | Content source | Approx. length |
|---|---------|----------------|----------------|
| Cover | UCP-style cover: UCP circular-seal logo + heading block + Shaheer's info (no supervisor line) | static + cover fields + `ucp_logo.jpg` | 1 page |
| 1 | Introduction | prose authored to match the sample's tone and length (~150 words) | 0.5–1 page |
| 2 | Selected Functional Modules | intro paragraph + 3 module blurbs | 1–1.5 pages |
| 3 | Original Logic Explanation | per-mode algorithm description | 1.5–2 pages |
| 4 | C Implementations | 3 code listings (30–50 lines each) from `src/analyzer.c` showing the Sequential / Pthread / OpenMP branches | 3–4 pages |
| 5 | GUI Frontend (Tkinter) | 1 code listing from `gui.py` (FrameAnalyzerApp skeleton + benchmark method) + 1 paragraph on the 3 tabs | 1–1.5 pages |
| 6 | System Specifications | real `lscpu` + `/proc/meminfo` + benchmark report header | 0.5–1 page |
| 7 | Build & Execution | `Makefile` content + CLI flags + GUI launch | 0.5–1 page |
| 8 | Test Workload & Figures | 20-frame generator description + 1 input/output figure pair | 1–1.5 pages |
| 9 | Completion Time Comparison | unified table from 4 captured runs + analysis | 1–1.5 pages |
| 10 | Conclusion | hand-written summary | 0.5–1 page |
| 11 | References (APA) | 6–8 entries | 0.5–1 page |

Target total: **14–18 pages** (sample is 14).

## Data sources (provenance)

Every value in the report must be traceable to one of the following.

### Code listings

- `src/analyzer.c:79-122` — the three mode dispatch branches (Sequential loop, Pthread worker spawn, OpenMP parallel for)
- `src/sobel.c:19-80` — the Sobel 3×3 convolution
- `src/ppm.c:23-102` — P3 PPM read (for the P3-format note in System Specs)
- `gui.py:1-50` — Tkinter app initialization, FrameAnalyzerApp class start

Each listing is trimmed to 30–50 lines (skipping comments and obvious scaffolding) and wrapped in a styled monospace block with a 1-line caption naming the source file and lines.

### System specifications

From real measurements on the development machine:

```
CPU Model       : Intel(R) Core(TM) i7-6820HQ CPU @ 2.70GHz
Physical Cores  : 4
Logical Threads : 8
Total Memory    : 15.5 GB
Kernel Version  : 6.18.33
Compiler        : gcc 15.2.0 with -O3 -fopenmp -lpthread
OpenMP Threads  : 8
```

Sourced from: `./bin/frame_analyzer --benchmark` (header block), `lscpu` (verifies 4C/8T), and `/proc/meminfo`.

### Timing table

Captured from 4 live runs (already executed during brainstorming, results in `/tmp/opencode/pdf_extract/benchmark_run.txt`):

| Mode | workers=1 | workers=2 | workers=4 | workers=8 |
|------|----------|----------|----------|----------|
| Sequential | 2714.66 ms | 2809.54 ms | 2713.84 ms | 2862.94 ms |
| Pthread | 2438.83 ms | 2182.31 ms | 1421.93 ms | 1162.16 ms |
| OpenMP | 2486.48 ms | 2726.28 ms | 2926.44 ms | 2703.53 ms |

All three modes produce **212,301 edge pixels** — the consistency check is highlighted in the Conclusion.

(Note: Sequential row varies slightly because the benchmark re-runs Seq for each `--workers N` value. The table presents each row from the matching benchmark run.)

### Figures

```
test_frames/frame_0000.ppm         ->  scripts/figures/input.png
test_frames_output/edge_frame_0000.ppm  ->  scripts/figures/output.png
```

Conversion uses Pillow (PIL) — no ImageMagick dependency:

```python
from PIL import Image
Image.open("test_frames/frame_0000.ppm").save("scripts/figures/input.png")
Image.open("test_frames_output/edge_frame_0000.ppm").save("scripts/figures/output.png")
```

If Pillow is unavailable, the generator script falls back to a hand-rolled PPM→PNG converter (no extra dependency).

Both are inserted side-by-side in Section 8 (Test Workload & Figures) with caption "Figure 1: Sample input frame (left) and its Sobel edge output (right). 512×512 P3 PPM, identical seed across all three modes."

## Build & execution (Section 7 of the report)

This section replaces the template's MPI LAN setup. Content:

- **Compiler:** `gcc` with `-O3 -Wall -Wextra -fopenmp`
- **Linker flags:** `-fopenmp -lpthread -lm`
- **Build:** `make` (produces `bin/frame_analyzer`)
- **CLI usage:**
  - `./bin/frame_analyzer --mode 1 --dir test_frames`
  - `./bin/frame_analyzer --mode 2 --dir test_frames --workers 4`
  - `./bin/frame_analyzer --mode 3 --dir test_frames`
  - `./bin/frame_analyzer --benchmark --dir test_frames --workers 4`
- **GUI launch:** `make gui` (builds + launches Tkinter)
- **Generate test frames:** `make generate` (20 random 512×512 P3 PPM)

## GUI section (its own dedicated "section 5" in the report)

Content: 1-paragraph description of the 3 tabs (Scanner, Scan History, Benchmark Report) + a trimmed `gui.py` listing showing the `FrameAnalyzerApp` class skeleton and one of the benchmark-run methods.

## References (APA, 6–8 entries)

1. OpenMP Architecture Review Board. (2024). *OpenMP 6.0 reference guide*. OpenMP.
2. IEEE Std 1003.1. (2018). *POSIX.1-2017 — Threads (`<pthread.h>`)*. The Open Group.
3. Sobel, I., & Feldman, G. (1968). *A 3×3 isotropic gradient operator for image processing*. Stanford Artificial Intelligence Project.
4. Amdahl, G. M. (1967). Validity of the single-processor approach to achieving large-scale computing capabilities. In *AFIPS Conference Proceedings* (Vol. 30, pp. 483–485). ACM.
5. Poskanzer, J. (n.d.). *P3 PPM image format specification*. Retrieved from Netpbm documentation.
6. Lundh, F., et al. (2024). *An Introduction to Tkinter* (Python documentation). Python Software Foundation.
7. Python Software Foundation. (2024). *Python 3.13 Language Reference*. Python Software Foundation.
8. Gustafson, J. L. (1988). Reevaluating Amdahl's law. *Communications of the ACM*, 31(5), 532–533.

## Error handling

| Failure | Behavior |
|---------|----------|
| `report_content.json` missing or malformed | Script aborts with a clear error message pointing at the path. |
| `python-docx` not installed | Script prints `pip install python-docx` and aborts. |
| ImageMagick `convert` not installed | Not a dependency — we use Pillow instead. |
| PPM → PNG conversion fails | Generator aborts before inserting figures; report still builds without them and prints a warning. |
| UCP logo download fails (`fetch_ucp_logo.sh` exit code != 0) | Script prints a warning and proceeds with the cover page rendered without the seal. |
| Output `.docx` already exists | Overwritten (no prompt — this is a generator). |

## Testing

This is a document-generation task. "Correct" means: the produced `.docx` opens cleanly in Word/LibreOffice, contains all 11 numbered sections + a cover, has a valid cover page, a 3-row × 4-column timing table, 4 code listings (3 C + 1 Python), 2 figures, and 6–8 references.

Verification steps after generation:

1. `unzip -l report.docx` — confirms a valid DOCX (zip) structure.
2. Open in LibreOffice headless: `libreoffice --headless --cat report.docx > /dev/null` — confirms it parses.
3. Spot-check the timing table against `/tmp/opencode/pdf_extract/benchmark_run.txt` (the 4 captured runs).
4. Spot-check the system specs against the benchmark report header.
5. Spot-check each code listing against the named source file + line range.

## Out of scope

- Generating a PDF (the user explicitly chose DOCX only).
- Authoring original research content (all content is either code, measured output, or generic description).
- Adding a bibliography manager (BibTeX, Zotero, etc.) — references are static APA strings in the JSON.
- Translating the cover page to anything other than English.
- A "Submitted to" line on the cover (the user has no supervisor; the field is omitted entirely).
- Generating an alternative UCP logo (e.g. monochrome / white-on-green variants); we use the one Wikipedia Commons provides.
