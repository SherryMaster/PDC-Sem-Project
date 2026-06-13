#!/usr/bin/env python3
"""
Parallel Batch Frame Analyzer — Cyberpunk Control Room Interface
Dark industrial aesthetic with electric cyan/magenta accents,
custom-styled widgets, and glowing terminal readouts.
"""
import os
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading

BINARY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "frame_analyzer")
DEFAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_frames")

# ─── Color Palette ───────────────────────────────────────────────────────────
BG_DARKEST  = "#06060c"
BG_DARK     = "#0c0c18"
BG_MID      = "#121224"
BG_PANEL    = "#141430"
BG_INPUT    = "#181840"
BG_HOVER    = "#1e1e4a"
CYAN        = "#00e5ff"
CYAN_DIM    = "#006878"
MAGENTA     = "#ff00aa"
MAGENTA_DIM = "#7a0055"
AMBER       = "#ffaa00"
GREEN       = "#00ff88"
RED         = "#ff3355"
TEXT_BRIGHT  = "#e0e0f0"
TEXT_DIM     = "#7a7a9a"
TEXT_MUTED   = "#4a4a6a"
BORDER       = "#252550"
BORDER_LIT   = "#3a3a80"

# ─── Fonts ───────────────────────────────────────────────────────────────────
FONT_MONO      = ("FiraCode Nerd Font Mono", 10)
FONT_MONO_SM   = ("FiraCode Nerd Font Mono", 9)
FONT_DISPLAY   = ("Hack", 13, "bold")
FONT_DISPLAY_SM = ("Hack", 10, "bold")
FONT_LABEL     = ("DejaVu Sans Mono", 10)
FONT_BTN       = ("DejaVu Sans Mono", 10, "bold")


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
        specs["GCC"] = result.stdout.strip().split("\n")[0]
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


# ─── Custom Widgets ──────────────────────────────────────────────────────────

class GlowButton(tk.Canvas):
    """Button with glowing border on hover and press effects."""

    def __init__(self, parent, text, command=None, color=CYAN, width=140, **kwargs):
        super().__init__(parent, highlightthickness=0, height=34, width=width,
                         bg=BG_DARKEST, bd=0, **kwargs)
        self.command = command
        self.color = color
        self.text = text
        self.hovered = False
        self.pressed = False
        self.disabled = False
        self.configure(cursor="hand2")
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10 or h < 10:
            return
        if self.disabled:
            # Dim outline
            self.create_rectangle(1, 1, w - 1, h - 1, outline=BORDER, width=1)
            self.create_rectangle(2, 2, w - 2, h - 2, fill=BG_PANEL, outline="")
            self.create_text(w // 2, h // 2, text=self.text,
                             fill=TEXT_MUTED, font=FONT_BTN)
            return

        if self.hovered:
            self.create_rectangle(4, 4, w - 4, h - 4, outline=BORDER, width=1)
            self.create_rectangle(3, 3, w - 3, h - 3, outline=BORDER_LIT, width=1)

        border = self.color if self.hovered else BORDER_LIT
        if self.pressed:
            border = MAGENTA
        self.create_rectangle(1, 1, w - 1, h - 1, outline=border, width=1)

        fill = BG_HOVER if self.hovered else (BG_INPUT if self.pressed else BG_PANEL)
        self.create_rectangle(2, 2, w - 2, h - 2, fill=fill, outline="")

        text_col = self.color if self.hovered else TEXT_BRIGHT
        if self.pressed:
            text_col = MAGENTA
        self.create_text(w // 2, h // 2, text=self.text, fill=text_col, font=FONT_BTN)

    def _on_enter(self, e):
        if not self.disabled:
            self.hovered = True
            self._draw()

    def _on_leave(self, e):
        self.hovered = False
        self.pressed = False
        self._draw()

    def _on_press(self, e):
        if not self.disabled:
            self.pressed = True
            self._draw()

    def _on_release(self, e):
        self.pressed = False
        self._draw()
        if not self.disabled and self.hovered and self.command:
            self.command()

    def set_state(self, state):
        self.disabled = (state == tk.DISABLED)
        self.configure(cursor="" if self.disabled else "hand2")
        self._draw()


class StatusLED(tk.Canvas):
    """Circular status indicator."""

    def __init__(self, parent, color=GREEN, **kwargs):
        super().__init__(parent, width=12, height=12, highlightthickness=0,
                         bg=BG_DARKEST, bd=0, **kwargs)
        self.led_color = color
        self._draw()

    def _draw(self):
        self.delete("all")
        self.create_oval(1, 1, 11, 11, outline=BORDER, width=1)
        self.create_oval(3, 3, 9, 9, fill=self.led_color, outline="")

    def set_color(self, color):
        self.led_color = color
        self._draw()


class TerminalOutput(tk.Frame):
    """Terminal-like output area with window chrome header."""

    def __init__(self, parent, title="OUTPUT", height=10, **kwargs):
        super().__init__(parent, bg=BG_DARKEST, **kwargs)

        header = tk.Frame(self, bg=BG_PANEL, height=26)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        dots = tk.Frame(header, bg=BG_PANEL)
        dots.pack(side=tk.LEFT, padx=(10, 0), pady=7)
        for c in [RED, AMBER, GREEN]:
            tk.Canvas(dots, width=8, height=8, bg=BG_PANEL,
                      highlightthickness=0).create_oval(1, 1, 7, 7, fill=c, outline="")
            tk.Canvas(dots, width=8, height=8, bg=BG_PANEL,
                      highlightthickness=0).pack(side=tk.LEFT, padx=2)

        tk.Label(header, text=title, font=FONT_DISPLAY_SM,
                 fg=TEXT_MUTED, bg=BG_PANEL).pack(side=tk.LEFT, padx=10)

        body_frame = tk.Frame(self, bg="#0a0a16")
        body_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            body_frame, height=height, font=FONT_MONO,
            bg="#0a0a16", fg=GREEN, insertbackground=GREEN,
            state=tk.DISABLED, relief=tk.FLAT, padx=12, pady=8,
            selectbackground=CYAN_DIM, selectforeground=TEXT_BRIGHT,
            borderwidth=0, highlightthickness=0, insertwidth=2,
            wrap=tk.WORD
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(body_frame, command=self.text.yview,
                          bg=BG_PANEL, troughcolor=BG_DARKEST,
                          activebackground=CYAN_DIM, width=8,
                          highlightthickness=0, bd=0)
        self.text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def set_content(self, text):
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
        self.text.configure(state=tk.DISABLED)


class LabeledEntry(tk.Frame):
    """Entry field with a label above it and focus glow."""

    def __init__(self, parent, label="", width=40, textvariable=None, **kw):
        super().__init__(parent, bg=BG_DARKEST, **kw)
        self.label = tk.Label(self, text=label, font=FONT_LABEL,
                              fg=TEXT_DIM, bg=BG_DARKEST, anchor="w")
        self.label.pack(fill=tk.X, pady=(0, 3))

        wrap = tk.Frame(self, bg=BORDER)
        wrap.pack(fill=tk.X)

        self.entry = tk.Entry(wrap, font=FONT_MONO, width=width,
                              bg=BG_INPUT, fg=TEXT_BRIGHT, insertbackground=CYAN,
                              relief=tk.FLAT, bd=4, highlightthickness=0,
                              textvariable=textvariable)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<FocusIn>", lambda e: (self.label.configure(fg=CYAN),
                                                wrap.configure(bg=CYAN)))
        self.entry.bind("<FocusOut>", lambda e: (self.label.configure(fg=TEXT_DIM),
                                                  wrap.configure(bg=BORDER)))

    def get(self):
        return self.entry.get()


class LabeledSpinbox(tk.Frame):
    """Spinbox with a label above it."""

    def __init__(self, parent, label="", from_=1, to=64, textvariable=None, **kw):
        super().__init__(parent, bg=BG_DARKEST, **kw)
        tk.Label(self, text=label, font=FONT_LABEL,
                 fg=TEXT_DIM, bg=BG_DARKEST, anchor="w").pack(fill=tk.X, pady=(0, 3))

        wrap = tk.Frame(self, bg=BORDER)
        wrap.pack(fill=tk.X)

        self.spinbox = tk.Spinbox(wrap, from_=from_, to=to, width=6,
                                   font=FONT_MONO, bg=BG_INPUT, fg=TEXT_BRIGHT,
                                   insertbackground=CYAN, relief=tk.FLAT, bd=4,
                                   buttonbackground=BG_PANEL, buttondownrelief=tk.FLAT,
                                   buttonuprelief=tk.FLAT, highlightthickness=0,
                                   textvariable=textvariable)
        self.spinbox.pack(fill=tk.X)

    def set_state(self, state):
        self.spinbox.configure(state=state)


# ─── Main Application ───────────────────────────────────────────────────────

class FrameAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PARALLEL BATCH FRAME ANALYZER // CONTROL INTERFACE")
        self.root.geometry("960x720")
        self.root.minsize(820, 620)
        self.root.configure(bg=BG_DARKEST)
        self.history = []
        self.report_data = None
        self.active_tab = "scanner"

        self._build_header()
        self._build_tab_bar()
        self._build_content_area()
        self._build_scanner_tab()
        self._build_history_tab()
        self._build_report_tab()
        self._build_status_bar()
        self._switch_tab("scanner")

    # ── Chrome ───────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=BG_PANEL)
        left.pack(side=tk.LEFT, padx=16, fill=tk.Y)
        tk.Frame(left, bg=CYAN, height=2, width=200).pack(anchor="w", pady=(6, 4))
        tk.Label(left, text="FRAME ANALYZER", font=FONT_DISPLAY,
                 fg=CYAN, bg=BG_PANEL).pack(anchor="w")
        tk.Label(left, text="PARALLEL COMPUTING LAB // EDGE DETECTION SYSTEM",
                 font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")

        right = tk.Frame(hdr, bg=BG_PANEL)
        right.pack(side=tk.RIGHT, padx=16, fill=tk.Y)
        row = tk.Frame(right, bg=BG_PANEL)
        row.pack(anchor="e", pady=14)
        self.header_led = StatusLED(row, color=GREEN)
        self.header_led.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(row, text="SYSTEM ONLINE", font=FONT_LABEL,
                 fg=GREEN, bg=BG_PANEL).pack(side=tk.LEFT)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

    def _build_tab_bar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=38)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        self.tab_buttons = {}
        self.tab_frames = {}
        for name, label in [("scanner", "SCANNER"), ("history", "HISTORY"), ("report", "BENCHMARK")]:
            btn = tk.Label(bar, text=label, font=FONT_LABEL, fg=TEXT_DIM,
                           bg=BG_PANEL, padx=24, pady=6, cursor="hand2")
            btn.pack(side=tk.LEFT)
            btn.bind("<Button-1>", lambda e, n=name: self._switch_tab(n))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=CYAN)
                     if self.tab_buttons.get(self.active_tab) != b else None)
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=TEXT_DIM)
                     if self.tab_buttons.get(self.active_tab) != b else None)
            self.tab_buttons[name] = btn

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

    def _build_content_area(self):
        self.content = tk.Frame(self.root, bg=BG_DARKEST)
        self.content.pack(fill=tk.BOTH, expand=True)

        self.tab_frames = {
            "scanner": tk.Frame(self.content, bg=BG_DARKEST),
            "history": tk.Frame(self.content, bg=BG_DARKEST),
            "report": tk.Frame(self.content, bg=BG_DARKEST),
        }

    def _switch_tab(self, name):
        if self.active_tab and self.active_tab in self.tab_frames:
            self.tab_frames[self.active_tab].pack_forget()
            b = self.tab_buttons.get(self.active_tab)
            if b:
                b.configure(fg=TEXT_DIM, bg=BG_PANEL)

        self.active_tab = name
        self.tab_buttons[name].configure(fg=CYAN, bg=BG_MID)
        self.tab_frames[name].pack(fill=tk.BOTH, expand=True)

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.status_label = tk.Label(bar, text="IDLE", font=FONT_MONO_SM,
                                     fg=TEXT_MUTED, bg=BG_PANEL)
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.time_label = tk.Label(bar, text="", font=FONT_MONO_SM,
                                   fg=TEXT_MUTED, bg=BG_PANEL)
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self._tick_clock()

    def _tick_clock(self):
        self.time_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    # ── Scanner Tab ──────────────────────────────────────────────────────

    def _build_scanner_tab(self):
        f = self.tab_frames["scanner"]

        # Directory panel
        p = tk.Frame(f, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        p.pack(fill=tk.X, padx=12, pady=(12, 6))
        tk.Label(p, text="INPUT DIRECTORY", font=FONT_DISPLAY_SM,
                 fg=CYAN, bg=BG_PANEL).pack(anchor="w", padx=10, pady=(8, 4))

        row = tk.Frame(p, bg=BG_PANEL)
        row.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.dir_var = tk.StringVar(value=DEFAULT_DIR)
        self.dir_entry = LabeledEntry(row, width=55, textvariable=self.dir_var)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        GlowButton(row, text="BROWSE", command=self._browse_dir, color=CYAN).pack(side=tk.LEFT)

        # Settings panel
        sp = tk.Frame(f, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        sp.pack(fill=tk.X, padx=12, pady=6)
        tk.Label(sp, text="EXECUTION SETTINGS", font=FONT_DISPLAY_SM,
                 fg=MAGENTA, bg=BG_PANEL).pack(anchor="w", padx=10, pady=(8, 4))

        row2 = tk.Frame(sp, bg=BG_PANEL)
        row2.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.mode_var = tk.StringVar(value="Sequential")
        mode_frame = tk.Frame(row2, bg=BG_DARKEST)
        mode_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(mode_frame, text="MODE", font=FONT_LABEL,
                 fg=TEXT_DIM, bg=BG_DARKEST).pack(anchor="w", pady=(0, 3))
        mode_wrap = tk.Frame(mode_frame, bg=BORDER)
        mode_wrap.pack(fill=tk.X)
        self.mode_menu = tk.OptionMenu(mode_wrap, self.mode_var,
                                        "Sequential", "Pthreads", "OpenMP")
        self.mode_menu.configure(
            font=FONT_MONO, bg=BG_INPUT, fg=TEXT_BRIGHT, activebackground=BG_HOVER,
            activeforeground=CYAN, highlightthickness=0, relief=tk.FLAT, bd=4,
            indicatoron=True, width=12
        )
        self.mode_menu["menu"].configure(
            bg=BG_PANEL, fg=TEXT_BRIGHT, activebackground=CYAN_DIM,
            activeforeground=TEXT_BRIGHT, relief=tk.FLAT, borderwidth=0, font=FONT_MONO
        )
        self.mode_menu.pack(fill=tk.X)

        self.workers_var = tk.IntVar(value=4)
        self.workers_spinbox = LabeledSpinbox(row2, label="WORKERS",
                                              from_=1, to=64,
                                              textvariable=self.workers_var)
        self.workers_spinbox.pack(side=tk.LEFT, padx=(0, 20))

        self.mode_indicator = tk.Label(row2, text="SINGLE-THREADED", font=FONT_LABEL,
                                       fg=AMBER, bg=BG_PANEL)
        self.mode_indicator.pack(side=tk.LEFT, padx=(0, 20))

        self.start_btn = GlowButton(row2, text="START SCAN", width=130,
                                    command=self._start_scan, color=GREEN)
        self.start_btn.pack(side=tk.RIGHT)

        self.mode_var.trace_add("write", lambda *_: self._on_mode_change())
        self._on_mode_change()

        # Results panel
        rp = tk.Frame(f, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        rp.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))
        tk.Label(rp, text="SCAN RESULTS", font=FONT_DISPLAY_SM,
                 fg=GREEN, bg=BG_PANEL).pack(anchor="w", padx=10, pady=(8, 4))

        self.result_terminal = TerminalOutput(rp, title="SCAN OUTPUT", height=10)
        self.result_terminal.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _on_mode_change(self, *args):
        mode = self.mode_var.get()
        if mode == "Pthreads":
            self.workers_spinbox.set_state(tk.NORMAL)
            self.mode_indicator.configure(text="MULTI-THREADED", fg=CYAN)
        elif mode == "OpenMP":
            self.workers_spinbox.set_state(tk.DISABLED)
            self.mode_indicator.configure(text="PARALLEL FOR", fg=MAGENTA)
        else:
            self.workers_spinbox.set_state(tk.DISABLED)
            self.mode_indicator.configure(text="SINGLE-THREADED", fg=AMBER)

    # ── History Tab ──────────────────────────────────────────────────────

    def _build_history_tab(self):
        f = self.tab_frames["history"]

        tk.Label(f, text="SCAN HISTORY", font=FONT_DISPLAY_SM,
                 fg=CYAN, bg=BG_DARKEST).pack(anchor="w", padx=12, pady=(12, 6))

        wrap = tk.Frame(f, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        cols = ("run", "mode", "workers", "frames", "pixels", "edge_pixels", "time_ms", "timestamp")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Cyber.Treeview",
                         background=BG_INPUT, foreground=TEXT_BRIGHT,
                         fieldbackground=BG_INPUT, font=FONT_MONO,
                         rowheight=30, borderwidth=0)
        style.configure("Cyber.Treeview.Heading",
                         background=BG_MID, foreground=CYAN,
                         font=FONT_LABEL, borderwidth=0, relief=tk.FLAT)
        style.map("Cyber.Treeview.Heading",
                   background=[("active", BG_HOVER)])
        style.map("Cyber.Treeview",
                   background=[("selected", CYAN_DIM)],
                   foreground=[("selected", TEXT_BRIGHT)])

        inner = tk.Frame(wrap, bg=BG_PANEL)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.tree = ttk.Treeview(inner, columns=cols, show="headings",
                                  style="Cyber.Treeview")
        hdrs = {"run": ("#", 45), "mode": ("MODE", 105), "workers": ("WORKERS", 75),
                "frames": ("FRAMES", 75), "pixels": ("TOTAL PX", 115),
                "edge_pixels": ("EDGE PX", 105), "time_ms": ("TIME (ms)", 100),
                "timestamp": ("TIMESTAMP", 165)}
        for col, (txt, w) in hdrs.items():
            self.tree.heading(col, text=txt)
            anchor = tk.E if col in ("pixels", "edge_pixels", "time_ms") else tk.CENTER
            self.tree.column(col, width=w, anchor=anchor)

        sb = ttk.Scrollbar(inner, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    # ── Report Tab ───────────────────────────────────────────────────────

    def _build_report_tab(self):
        f = self.tab_frames["report"]

        # Settings bar
        sp = tk.Frame(f, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        sp.pack(fill=tk.X, padx=12, pady=(12, 6))
        tk.Label(sp, text="BENCHMARK CONFIGURATION", font=FONT_DISPLAY_SM,
                 fg=MAGENTA, bg=BG_PANEL).pack(anchor="w", padx=10, pady=(8, 4))

        row = tk.Frame(sp, bg=BG_PANEL)
        row.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.report_dir_var = tk.StringVar(value=DEFAULT_DIR)
        LabeledEntry(row, width=38, textvariable=self.report_dir_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        GlowButton(row, text="BROWSE", command=self._browse_report_dir,
                    color=CYAN).pack(side=tk.LEFT, padx=(0, 20))

        self.report_workers_var = tk.IntVar(value=4)
        LabeledSpinbox(row, label="PTHREADS", from_=1, to=64,
                       textvariable=self.report_workers_var).pack(side=tk.LEFT, padx=(0, 20))

        GlowButton(row, text="RUN BENCHMARK", width=150,
                    command=self._run_benchmark, color=MAGENTA).pack(side=tk.LEFT, padx=(0, 8))
        self.export_btn = GlowButton(row, text="EXPORT", width=90,
                                     command=self._export_report, color=AMBER)
        self.export_btn.pack(side=tk.LEFT)

        # Paned window
        paned = tk.PanedWindow(f, orient=tk.HORIZONTAL, bg=BG_DARKEST,
                                sashwidth=6, sashrelief=tk.FLAT, borderwidth=0)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))

        # Left: specs
        lp = tk.Frame(paned, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(lp, text="SYSTEM SPECS", font=FONT_DISPLAY_SM,
                 fg=AMBER, bg=BG_PANEL).pack(anchor="w", padx=10, pady=(8, 4))
        self.specs_terminal = TerminalOutput(lp, title="SYSINFO", height=10)
        self.specs_terminal.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        paned.add(lp, minsize=240, width=300)

        # Right: results
        rp = tk.Frame(paned, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(rp, text="BENCHMARK RESULTS", font=FONT_DISPLAY_SM,
                 fg=GREEN, bg=BG_PANEL).pack(anchor="w", padx=10, pady=(8, 4))
        self.report_terminal = TerminalOutput(rp, title="BENCHMARK OUTPUT", height=10)
        self.report_terminal.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        paned.add(rp, minsize=300)

    # ── Actions ──────────────────────────────────────────────────────────

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _browse_report_dir(self):
        d = filedialog.askdirectory(initialdir=self.report_dir_var.get())
        if d:
            self.report_dir_var.set(d)

    def _start_scan(self):
        dirpath = self.dir_entry.get().strip()
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
        cmd = [BINARY, "--mode", str(mode_map[mode]), "--dir", dirpath]
        if mode == "Pthreads":
            cmd.extend(["--workers", str(self.workers_var.get())])

        self.start_btn.set_state(tk.DISABLED)
        self.header_led.set_color(AMBER)
        self.status_label.configure(text=f"SCANNING // {mode.upper()}", fg=AMBER)
        self.result_terminal.set_content(
            f"{'='*50}\n"
            f"  MODE     : {mode}\n"
            f"  DIRECTORY: {dirpath}\n"
            f"{'='*50}\n\n"
            f"Running...\n"
        )
        self.root.update_idletasks()

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            self._finish_scan("ERROR: Execution timed out (300s limit).")
            return
        except Exception as e:
            self._finish_scan(f"ERROR: {e}")
            return

        if result.returncode != 0:
            self._finish_scan(f"ERROR (exit code {result.returncode}):\n{result.stderr}\n{result.stdout}")
        else:
            self._finish_scan(result.stdout.strip())
            self._parse_and_log(result.stdout.strip(), mode, self.workers_var.get())

    def _finish_scan(self, text):
        self.result_terminal.set_content(text)
        self.start_btn.set_state(tk.NORMAL)
        self.header_led.set_color(GREEN)
        self.status_label.configure(text="SCAN COMPLETE", fg=GREEN)
        self.root.after(3000, lambda: self.status_label.configure(text="IDLE", fg=TEXT_MUTED))

    def _parse_and_log(self, output, mode, workers):
        parsed = {}
        for part in output.split(" | "):
            if ":" in part:
                k, v = part.split(":", 1)
                parsed[k.strip()] = v.strip()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "run": len(self.history) + 1,
            "mode": parsed.get("MODE", mode),
            "workers": parsed.get("WORKERS", str(workers)),
            "frames": parsed.get("FRAMES", "?"),
            "pixels": parsed.get("PIXELS", "?"),
            "edge_pixels": parsed.get("EDGE_PIXELS", "?"),
            "time_ms": parsed.get("TOTAL_TIME", "?"),
            "timestamp": ts,
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

        cmd = [BINARY, "--benchmark", "--dir", dirpath,
               "--workers", str(self.report_workers_var.get())]

        self.start_btn.set_state(tk.DISABLED) if hasattr(self, "start_btn") else None
        self.export_btn.set_state(tk.DISABLED)
        self.header_led.set_color(MAGENTA)
        self.status_label.configure(text="BENCHMARKING // ALL MODES", fg=MAGENTA)
        self.report_terminal.set_content(
            "BENCHMARK IN PROGRESS\n"
            "Running Sequential + Pthreads + OpenMP...\n"
            "This may take a moment.\n"
        )
        self.specs_terminal.set_content("Collecting system information...\n")
        self.root.update_idletasks()

        def worker():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                self.root.after(0, lambda: self._on_bench_done(result))
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self._on_bench_error("Timed out (600s)."))
            except Exception as e:
                self.root.after(0, lambda: self._on_bench_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_bench_error(self, msg):
        self.start_btn.set_state(tk.NORMAL)
        self.header_led.set_color(RED)
        self.status_label.configure(text="BENCHMARK FAILED", fg=RED)
        self.report_terminal.set_content(f"ERROR: {msg}\n")
        self.root.after(3000, lambda: self.status_label.configure(text="IDLE", fg=TEXT_MUTED))

    def _on_bench_done(self, result):
        self.start_btn.set_state(tk.NORMAL)
        if result.returncode != 0:
            self._on_bench_error(f"Exit code {result.returncode}")
            self.report_terminal.set_content(f"{result.stderr}\n{result.stdout}")
            return

        output = result.stdout
        self.report_data = output
        self.export_btn.set_state(tk.NORMAL)
        specs, body = self._split_report(output)
        self.specs_terminal.set_content(specs)
        self.report_terminal.set_content(body)
        self.header_led.set_color(GREEN)
        self.status_label.configure(text="BENCHMARK COMPLETE", fg=GREEN)
        self.root.after(3000, lambda: self.status_label.configure(text="IDLE", fg=TEXT_MUTED))

    def _split_report(self, output):
        lines = output.split("\n")
        specs, report = [], []
        in_sys = in_rpt = False
        for line in lines:
            if "SYSTEM INFORMATION" in line:
                in_sys, in_rpt = True, False
                specs.append(line)
                continue
            if "END OF REPORT" in line:
                in_sys, in_rpt = False, False
                report.append(line)
                continue
            if "COMPARISON SUMMARY" in line:
                in_sys, in_rpt = False, True
            if "ANALYSIS" in line or "WORKLOAD" in line:
                in_rpt = True
            (specs if in_sys else report).append(line)
        return "\n".join(specs), "\n".join(report)

    def _export_report(self):
        if not self.report_data:
            messagebox.showinfo("No Data", "Run a benchmark first before exporting.")
            return
        fp = filedialog.asksaveasfilename(
            title="Export Benchmark Report",
            defaultextension=".txt",
            filetypes=[("Text Report", "*.txt"), ("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
            initialfile=f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if not fp:
            return
        if fp.endswith(".csv"):
            self._export_csv(fp)
        else:
            self._export_text(fp)
        messagebox.showinfo("Exported", f"Report saved to:\n{fp}")

    def _export_text(self, fp):
        with open(fp, "w") as f:
            f.write(self.report_data)
            f.write("\n\n--- Additional System Info (from Python) ---\n")
            for k, v in get_system_specs().items():
                f.write(f"  {k}: {v}\n")

    def _export_csv(self, fp):
        import csv
        specs = get_system_specs()
        with open(fp, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["PARALLEL BATCH FRAME ANALYZER - BENCHMARK REPORT"])
            w.writerow([])
            w.writerow(["SYSTEM INFORMATION"])
            for k, v in specs.items():
                w.writerow([k, v])
            w.writerow([])
            w.writerow(["COMPARISON RESULTS"])
            w.writerow(["Mode", "Time (ms)", "Workers", "Frames", "Total Pixels", "Edge Pixels", "Speedup"])
            for line in self.report_data.split("\n"):
                line = line.strip()
                if "|" in line and "---" not in line and "Mode" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 5:
                        w.writerow(parts)
            w.writerow([])
            w.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])


def main():
    root = tk.Tk()
    FrameAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
