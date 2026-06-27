#!/usr/bin/env python3
"""Generate report.docx from report_content.json + figures."""
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONTENT_PATH = SCRIPT_DIR / "report_content.json"
LOGO_PATH = SCRIPT_DIR / "figures" / "ucp_logo.jpg"
OUTPUT_PATH = PROJECT_ROOT / "report.docx"


def load_content() -> dict:
    with open(CONTENT_PATH) as f:
        return json.load(f)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT


def add_body(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(8)


def build_cover(doc: Document, content: dict) -> None:
    cover = content["cover"]

    if LOGO_PATH.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(LOGO_PATH), width=Inches(2.0))

    title_blocks = [
        cover["university"],
        cover["program"],
        cover["project_type"],
    ]
    for line in title_blocks:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.bold = True
        run.font.size = Pt(20 if line == cover["university"] else 16)

    doc.add_paragraph()
    topic_p = doc.add_paragraph()
    topic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    topic_run = topic_p.add_run("Topic: " + cover["topic"])
    topic_run.bold = True
    topic_run.font.size = Pt(14)

    doc.add_paragraph()
    doc.add_paragraph()

    info_lines = [
        f"Submitted by: {cover['submitted_by_name']}",
        f"Registration Number: {cover['submitted_by_reg']}",
        f"Degree Program: {cover['submitted_by_degree']}",
        f"Tools Used: {cover['tools']}",
    ]
    for line in info_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(line)
        run.font.size = Pt(13)

    doc.add_page_break()


def build_introduction(doc: Document, content: dict) -> None:
    add_heading(doc, "1. Introduction", level=1)
    add_body(doc, content["introduction"])


def main() -> int:
    if not CONTENT_PATH.exists():
        print(f"ERROR: missing {CONTENT_PATH}", file=sys.stderr)
        return 1

    content = load_content()
    doc = Document()

    build_cover(doc, content)
    build_introduction(doc, content)

    doc.save(str(OUTPUT_PATH))
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
