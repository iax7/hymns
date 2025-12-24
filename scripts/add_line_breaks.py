#!/usr/bin/env python3
"""Ensure every non-blank body line in content/*.md ends with exactly two
trailing spaces, so Markdown renders them as hard line breaks.

Frontmatter (between the leading --- markers) is left untouched.
"""
import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


def process(text: str) -> str:
    lines = text.split("\n")
    out = []
    in_frontmatter = False
    frontmatter_done = False

    for i, line in enumerate(lines):
        if not frontmatter_done and line.strip() == "---":
            in_frontmatter = not in_frontmatter
            if not in_frontmatter:
                frontmatter_done = True
            out.append(line)
            continue

        if in_frontmatter or not frontmatter_done:
            out.append(line)
            continue

        stripped = line.rstrip()
        if stripped == "":
            out.append("")
        else:
            out.append(stripped + "  ")

    return "\n".join(out)


def main():
    changed = 0
    for path in sorted(CONTENT_DIR.glob("*.md")):
        original = path.read_text(encoding="utf-8")
        updated = process(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"updated {path.relative_to(CONTENT_DIR.parent)}")
    print(f"done: {changed} file(s) changed")


if __name__ == "__main__":
    main()
