#!/usr/bin/env python3
import os
import subprocess
import sys
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading

BINARY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "frame_analyzer")
DEFAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_frames")


def get_system_specs():
    specs = {}
    specs["Platform"] = f"{platform.system()} {platform.release()}"
    specs["Machine"] = platform.machine()
    specs["Processor"] = platform.processor() or "N/A"
    specs["Python"] = platform.python_version()
    specs["Hostname"] = platform.node()

    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("model name"):
                    specs["CPU Model"] = line.split(":")[1].strip()
                    break
    except Exception:
        specs["CPU Model"] = platform.processor() or "Unknown"

    try:
        with open("/proc/cpuinfo", "r") as f:
            content = f.read()
            specs["Logical CPUs"] = content.count("processor")
    except Exception:
        specs["Logical CPUs"] = os.cpu_count() or "Unknown"

    try:
        with open("/proc/cpuinfo", "r") as f:
            content = f.read()
            core_ids = set()
            for line in content.split("\n"):
                if line.startswith("core id"):
                    core_ids.add(line.split(":")[1].strip())
            physical = len(core_ids)
            if physical == 0:
                physical = specs.get("Logical CPUs", "Unknown")
            specs["Physical Cores"] = physical
    except Exception:
        specs["Physical Cores"] = "Unknown"

    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    specs["Total Memory"] = f"{kb / 1048576:.1f} GB"
                    break
    except Exception:
        specs["Total Memory"] = "Unknown"

    try:
        result = subprocess.run(["gcc", "--version"], capture_output=True, text=True, timeout=5)
        first_line = result.stdout.strip().split("\n")[0]
        specs["GCC"] = first_line
    except Exception:
        specs["GCC"] = "Not found"

    try:
        result = subprocess.run(["uname", "-r"], capture_output=True, text=True, timeout=5)
        specs["Kernel"] = result.stdout.strip()
    except Exception:
        specs["Kernel"] = "Unknown"

    try:
        result = subprocess.run(["nproc"], capture_output=True, text=True, timeout=5)
        specs["OMP Available Threads"] = result.stdout.strip()
    except Exception:
        specs["OMP Available Threads"] = os.cpu_count() or "Unknown"

    return specs


class FrameAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parallel Batch Frame Analyzer")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        self.history = []
        self.report_data = None

        self._apply_theme()

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.scanner_frame = ttk.Frame(notebook)
        notebook.add(self.scanner_frame, text="  Scanner  ")
        self.history_frame = ttk.Frame(notebook)
        notebook.add(self.history_frame, text="  Scan History  ")
        self.report_frame = ttk.Frame(notebook)
        notebook.add(self.report_frame, text="  Benchmark Report  ")

        self._build_scanner_tab()
        self._build_history_tab()
        self._build_report_tab()

    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Result.TLabel", font=("Consolas", 11))
        style.configure("Treeview", font=("Consolas", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Report.TLabel", font=("Consolas", 10))
        style.configure("SpeedGreen.TLabel", font=("Consolas", 11, "bold"), foreground="#228B22")
        style.configure("SpeedRed.TLabel", font=("Consolas", 11, "bold"), foreground="#B22222")
        style.configure("SpecTitle.TLabel", font=("Segoe UI", 11, "bold"))
        self.root.configure(bg="#f0f0f0")

    def _build_scanner_tab(self):
        frame = self.scanner_frame

        dir_frame = ttk.LabelFrame(frame, text="Input Directory", padding=8)
        dir_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.dir_var = tk.StringVar(value=DEFAULT_DIR)
        ttk.Label(dir_frame, text="Path:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=60).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self._browse_dir).pack(side=tk.LEFT)

        ctrl_frame = ttk.LabelFrame(frame, text="Execution Settings", padding=8)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(ctrl_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        self.mode_var = tk.StringVar(value="Sequential")
        mode_menu = ttk.Combobox(ctrl_frame, textvariable=self.mode_var,
                                  values=["Sequential", "Pthreads", "OpenMP"],
                                  state="readonly", width=15)
        mode_menu.pack(side=tk.LEFT, padx=(0, 15))
        mode_menu.bind("<<ComboboxSelected>>", self._on_mode_change)

        self.workers_label = ttk.Label(ctrl_frame, text="Workers:")
        self.workers_label.pack(side=tk.LEFT, padx=(0, 5))
        self.workers_var = tk.IntVar(value=4)
        self.workers_spin = ttk.Spinbox(ctrl_frame, from_=1, to=64,
                                         textvariable=self.workers_var, width=5)
        self.workers_spin.pack(side=tk.LEFT, padx=(0, 15))

        self.start_btn = ttk.Button(ctrl_frame, text="Start Scan", command=self._start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self._on_mode_change()

        result_frame = ttk.LabelFrame(frame, text="Results", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.result_text = tk.Text(result_frame, height=10, font=("Consolas", 11),
                                    bg="#1e1e1e", fg="#00ff00", insertbackground="white",
                                    state=tk.DISABLED, relief=tk.FLAT, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def _build_history_tab(self):
        frame = self.history_frame

        columns = ("run", "mode", "workers", "frames", "pixels", "edge_pixels", "time_ms", "timestamp")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)

        self.tree.heading("run", text="#")
        self.tree.heading("mode", text="Mode")
        self.tree.heading("workers", text="Workers")
        self.tree.heading("frames", text="Frames")
        self.tree.heading("pixels", text="Total Pixels")
        self.tree.heading("edge_pixels", text="Edge Pixels")
        self.tree.heading("time_ms", text="Time (ms)")
        self.tree.heading("timestamp", text="Timestamp")

        self.tree.column("run", width=40, anchor=tk.CENTER)
        self.tree.column("mode", width=100, anchor=tk.CENTER)
        self.tree.column("workers", width=70, anchor=tk.CENTER)
        self.tree.column("frames", width=70, anchor=tk.CENTER)
        self.tree.column("pixels", width=110, anchor=tk.E)
        self.tree.column("edge_pixels", width=110, anchor=tk.E)
        self.tree.column("time_ms", width=100, anchor=tk.E)
        self.tree.column("timestamp", width=160, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

    def _build_report_tab(self):
        frame = self.report_frame

        top_row = ttk.Frame(frame)
        top_row.pack(fill=tk.X, padx=10, pady=(10, 5))

        dir_frame = ttk.LabelFrame(top_row, text="Benchmark Settings", padding=8)
        dir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        inner = ttk.Frame(dir_frame)
        inner.pack(fill=tk.X)

        ttk.Label(inner, text="Directory:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.report_dir_var = tk.StringVar(value=DEFAULT_DIR)
        ttk.Entry(inner, textvariable=self.report_dir_var, width=45).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(inner, text="Browse", command=self._browse_report_dir).grid(row=0, column=2)

        ttk.Label(inner, text="Pthreads Workers:").grid(row=1, column=0, padx=(0, 5), pady=(5, 0), sticky=tk.W)
        self.report_workers_var = tk.IntVar(value=4)
        ttk.Spinbox(inner, from_=1, to=64, textvariable=self.report_workers_var, width=5).grid(
            row=1, column=1, sticky=tk.W, pady=(5, 0))

        btn_frame = ttk.Frame(top_row)
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))

        self.run_bench_btn = ttk.Button(btn_frame, text="Run Benchmark", command=self._run_benchmark)
        self.run_bench_btn.pack(pady=(0, 5))

        self.export_btn = ttk.Button(btn_frame, text="Export Report", command=self._export_report,
                                      state=tk.DISABLED)
        self.export_btn.pack()

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        left_frame = ttk.LabelFrame(paned, text="System Information", padding=8)
        paned.add(left_frame, weight=1)

        self.specs_text = tk.Text(left_frame, font=("Consolas", 10), bg="#fafafa",
                                   state=tk.DISABLED, relief=tk.FLAT, padx=8, pady=8, width=35)
        self.specs_text.pack(fill=tk.BOTH, expand=True)

        right_frame = ttk.LabelFrame(paned, text="Benchmark Results", padding=8)
        paned.add(right_frame, weight=2)

        self.report_text = tk.Text(right_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#00ff00",
                                    insertbackground="white", state=tk.DISABLED, relief=tk.FLAT,
                                    padx=10, pady=10)
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def _on_mode_change(self, event=None):
        mode = self.mode_var.get()
        if mode == "Pthreads":
            self.workers_label.config(state=tk.NORMAL)
            self.workers_spin.config(state=tk.NORMAL)
        else:
            self.workers_label.config(state=tk.DISABLED)
            self.workers_spin.config(state=tk.DISABLED)

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _browse_report_dir(self):
        d = filedialog.askdirectory(initialdir=self.report_dir_var.get())
        if d:
            self.report_dir_var.set(d)

    def _start_scan(self):
        dirpath = self.dir_var.get().strip()
        if not dirpath:
            messagebox.showerror("Error", "Please enter a directory path.")
            return
        if not os.path.isdir(dirpath):
            messagebox.showerror("Error", f"Directory not found:\n{dirpath}")
            return
        if not os.path.isfile(BINARY):
            messagebox.showerror("Error",
                f"C binary not found at:\n{BINARY}\n\nRun 'make' first to compile.")
            return

        mode = self.mode_var.get()
        mode_map = {"Sequential": 1, "Pthreads": 2, "OpenMP": 3}
        mode_num = mode_map[mode]
        workers = self.workers_var.get()

        cmd = [BINARY, "--mode", str(mode_num), "--dir", dirpath]
        if mode == "Pthreads":
            cmd.extend(["--workers", str(workers)])

        self.start_btn.config(state=tk.DISABLED)
        self._set_result("Running...\n")

        self.root.update_idletasks()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            self._set_result("ERROR: Execution timed out (300s limit).\n")
            self.start_btn.config(state=tk.NORMAL)
            return
        except Exception as e:
            self._set_result(f"ERROR: {e}\n")
            self.start_btn.config(state=tk.NORMAL)
            return

        self.start_btn.config(state=tk.NORMAL)

        output = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            self._set_result(f"ERROR (exit code {result.returncode}):\n{stderr}\n{output}")
            return

        self._set_result(output + "\n")
        self._parse_and_log(output, mode, workers)

    def _set_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

    def _parse_and_log(self, output, mode, workers):
        parsed = {}
        for part in output.split(" | "):
            if ":" in part:
                key, val = part.split(":", 1)
                parsed[key.strip()] = val.strip()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = {
            "run": len(self.history) + 1,
            "mode": parsed.get("MODE", mode),
            "workers": parsed.get("WORKERS", str(workers)),
            "frames": parsed.get("FRAMES", "?"),
            "pixels": parsed.get("PIXELS", "?"),
            "edge_pixels": parsed.get("EDGE_PIXELS", "?"),
            "time_ms": parsed.get("TOTAL_TIME", "?"),
            "timestamp": timestamp,
        }
        self.history.append(entry)

        self.tree.insert("", tk.END, values=(
            entry["run"], entry["mode"], entry["workers"],
            entry["frames"], entry["pixels"], entry["edge_pixels"],
            entry["time_ms"], entry["timestamp"]
        ))

    def _run_benchmark(self):
        dirpath = self.report_dir_var.get().strip()
        if not dirpath:
            messagebox.showerror("Error", "Please enter a directory path.")
            return
        if not os.path.isdir(dirpath):
            messagebox.showerror("Error", f"Directory not found:\n{dirpath}")
            return
        if not os.path.isfile(BINARY):
            messagebox.showerror("Error",
                f"C binary not found at:\n{BINARY}\n\nRun 'make' first to compile.")
            return

        workers = self.report_workers_var.get()

        cmd = [BINARY, "--benchmark", "--dir", dirpath, "--workers", str(workers)]

        self.run_bench_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self._set_report_text("Running benchmark (Sequential + Pthreads + OpenMP)...\nThis may take a moment.\n")
        self._set_specs_text("Collecting system information...\n")

        self.root.update_idletasks()

        def run_in_thread():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                self.root.after(0, lambda: self._on_benchmark_done(result))
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self._on_benchmark_error("Benchmark timed out (600s)."))
            except Exception as e:
                self.root.after(0, lambda: self._on_benchmark_error(str(e)))

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def _on_benchmark_error(self, msg):
        self.run_bench_btn.config(state=tk.NORMAL)
        self._set_report_text(f"ERROR: {msg}\n")

    def _on_benchmark_done(self, result):
        self.run_bench_btn.config(state=tk.NORMAL)

        if result.returncode != 0:
            self._set_report_text(f"ERROR (exit code {result.returncode}):\n{result.stderr}\n{result.stdout}")
            return

        output = result.stdout
        self.report_data = output
        self.export_btn.config(state=tk.NORMAL)

        specs, report_body = self._split_report(output)
        self._set_specs_text(specs)
        self._set_report_text(report_body)

    def _split_report(self, output):
        lines = output.split("\n")
        specs_lines = []
        report_lines = []
        in_system = False
        in_report = False

        for line in lines:
            if "SYSTEM INFORMATION" in line:
                in_system = True
                in_report = False
                specs_lines.append(line)
                continue
            if "END OF REPORT" in line:
                in_system = False
                in_report = False
                report_lines.append(line)
                continue
            if "COMPARISON SUMMARY" in line:
                in_system = False
                in_report = True
            if "ANALYSIS" in line or "WORKLOAD" in line:
                in_report = True

            if in_system:
                specs_lines.append(line)
            else:
                report_lines.append(line)

        return "\n".join(specs_lines), "\n".join(report_lines)

    def _set_specs_text(self, text):
        self.specs_text.config(state=tk.NORMAL)
        self.specs_text.delete("1.0", tk.END)
        self.specs_text.insert(tk.END, text)
        self.specs_text.config(state=tk.DISABLED)

    def _set_report_text(self, text):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, text)
        self.report_text.config(state=tk.DISABLED)

    def _export_report(self):
        if not self.report_data:
            messagebox.showinfo("No Data", "Run a benchmark first before exporting.")
            return

        filetypes = [
            ("Text Report", "*.txt"),
            ("CSV Spreadsheet", "*.csv"),
            ("All Files", "*.*"),
        ]

        filepath = filedialog.asksaveasfilename(
            title="Export Benchmark Report",
            defaultextension=".txt",
            filetypes=filetypes,
            initialfile=f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if not filepath:
            return

        if filepath.endswith(".csv"):
            self._export_csv(filepath)
        else:
            self._export_text(filepath)

        messagebox.showinfo("Exported", f"Report saved to:\n{filepath}")

    def _export_text(self, filepath):
        with open(filepath, "w") as f:
            f.write(self.report_data)
            f.write("\n\n--- Additional System Info (from Python) ---\n")
            specs = get_system_specs()
            for key, val in specs.items():
                f.write(f"  {key}: {val}\n")

    def _export_csv(self, filepath):
        import csv
        specs = get_system_specs()

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow(["PARALLEL BATCH FRAME ANALYZER - BENCHMARK REPORT"])
            writer.writerow([])
            writer.writerow(["SYSTEM INFORMATION"])
            for key, val in specs.items():
                writer.writerow([key, val])
            writer.writerow([])

            writer.writerow(["COMPARISON RESULTS"])
            writer.writerow(["Mode", "Time (ms)", "Workers", "Frames", "Total Pixels", "Edge Pixels", "Speedup"])

            lines = self.report_data.split("\n")
            for line in lines:
                line = line.strip()
                if "|" in line and "---" not in line and "Mode" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 5:
                        writer.writerow(parts)

            writer.writerow([])
            writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])


def main():
    root = tk.Tk()
    app = FrameAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
