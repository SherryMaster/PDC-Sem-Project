#!/usr/bin/env python3
"""Convert sample PPM input/output frames to PNG for the report figures."""
import os
import sys
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
INPUT_PPM = PROJECT_ROOT / "test_frames" / "frame_0000.ppm"
OUTPUT_PPM = PROJECT_ROOT / "test_frames_output" / "edge_frame_0000.ppm"
INPUT_PNG = SCRIPT_DIR / "input.png"
OUTPUT_PNG = SCRIPT_DIR / "output.png"


def convert(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing PPM: {src}")
    img = Image.open(src)
    img.save(dst, "PNG")
    print(f"  {src.name} -> {dst.name}  ({dst.stat().st_size} bytes)")


def main() -> int:
    print(f"Converting figures into {SCRIPT_DIR} ...")
    convert(INPUT_PPM, INPUT_PNG)
    convert(OUTPUT_PPM, OUTPUT_PNG)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
