#!/usr/bin/env python3
"""Verify report.docx contains expected sections and content."""
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT = PROJECT_ROOT / "report.docx"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extract_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
    paragraphs = []
    for p in tree.getroot().iter(f"{{{NS['w']}}}p"):
        text = "".join(t.text or "" for t in p.iter(f"{{{NS['w']}}}t"))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n".join(paragraphs)


def main() -> int:
    if not REPORT.exists():
        print(f"FAIL: {REPORT} does not exist")
        return 1

    try:
        text = extract_text(REPORT)
    except Exception as e:
        print(f"FAIL: cannot read {REPORT}: {e}")
        return 1

    checks = [
        ("cover.university", "UNIVERSITY OF CENTRAL PUNJAB"),
        ("cover.name", "Shaheer Ahmed"),
        ("cover.reg", "L1F23BSAI0005"),
        ("cover.degree", "BS Artificial Intelligence"),
        ("intro.heading", "1. Introduction"),
        ("conclusion.heading", "10. Conclusion"),
        ("references.heading", "11. References"),
    ]
    failed = []
    for label, needle in checks:
        if needle not in text:
            failed.append(label)
            print(f"  FAIL: missing {label!r} (looking for {needle!r})")
        else:
            print(f"  OK:   {label}")

    if failed:
        print(f"\n{len(failed)} check(s) failed")
        return 1
    print(f"\nAll {len(checks)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
