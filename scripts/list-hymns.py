#!/usr/bin/env python3
"""List all hymns with their rendered line counts, sorted by ID.

Useful for manually tuning LONG_HYMN_THRESHOLD in build-pdf.sh. Unlike a
plain source-line count, this accounts for lines that are wide enough to
wrap onto an extra rendered line in the PDF's two-column layout, by
measuring real glyph widths with the actual EB Garamond font.
"""
import math
import re
import subprocess
import sys
from pathlib import Path

from PIL import ImageFont

GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

FONT_SIZE_PT = 14
PT_TO_IN = 1 / 72.27
MARGIN_CM = 1.5
COLUMNSEP_CM = 1.0
PAGE_WIDTH_IN = 8.5
CM_TO_IN = 1 / 2.54

FRONTMATTER_MARKER = re.compile(r"^---$")


def column_width_in():
    margin_in = MARGIN_CM * CM_TO_IN
    columnsep_in = COLUMNSEP_CM * CM_TO_IN
    body_width_in = PAGE_WIDTH_IN - 2 * margin_in
    return (body_width_in - columnsep_in) / 2


def find_font():
    try:
        path = subprocess.run(
            ["kpsewhich", "EBGaramond-Regular.otf"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        path = ""

    if not path:
        print("Error: EBGaramond-Regular.otf not found via kpsewhich "
              "(is texlive/ebgaramond installed?)", file=sys.stderr)
        sys.exit(1)

    return ImageFont.truetype(path, 200)


def body_lines(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    delimiters = [i for i, l in enumerate(lines) if FRONTMATTER_MARKER.match(l)]
    if len(delimiters) < 2:
        return []
    return lines[delimiters[1] + 1:]


def rendered_line_count(lines, font, col_width_in):
    # Base count matches the original line-counting behavior (every source
    # line, blank or not), so LONG_HYMN_THRESHOLD stays comparable. On top
    # of that, add the extra rendered lines contributed by lines wide
    # enough to wrap onto a second (or further) line in the PDF column.
    count = len(lines)
    for line in lines:
        text = line.strip()
        if not text:
            continue
        clean = text.replace("**", "").replace("//", "").replace("*", "")
        width_in = (font.getlength(clean) / 200) * (FONT_SIZE_PT * PT_TO_IN)
        count += max(0, math.ceil(width_in / col_width_in) - 1)
    return count


def extract_id(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("id:"):
            return int(line.split(":", 1)[1].strip())
    return None


def extract_title(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Title:"):
            return line.split(":", 1)[1].strip().strip('"')
    return "Untitled"


def main():
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 44

    font = find_font()
    col_width_in = column_width_in()

    content_dir = Path("content")
    hymns = []
    for path in content_dir.glob("*.md"):
        hymn_id = extract_id(path)
        if hymn_id is None:
            continue
        title = extract_title(path)
        lines = body_lines(path)
        count = rendered_line_count(lines, font, col_width_in)
        hymns.append((hymn_id, title, count))

    hymns.sort(key=lambda h: h[0])

    print(f"{BOLD}{'ID':<4}  {'TYPE':<6}  {'LINES':<5}  {'TITLE'}{RESET}")
    print(f"{'----':<4}  {'------':<6}  {'-----':<5}  {'-----'}")

    for hymn_id, title, count in hymns:
        if count > threshold:
            color, type_ = RED, "LONG"
        else:
            color, type_ = GREEN, "short"
        print(f"{color}{hymn_id:<4}  {type_:<6}  {count:<5}  {title}{RESET}")

    print()
    print(f"Threshold: {threshold} lines  (run with a number to change, e.g.: {sys.argv[0]} 40)")


if __name__ == "__main__":
    main()
