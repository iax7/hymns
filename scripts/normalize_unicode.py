#!/usr/bin/env python3
"""Normalize content/*.md to NFC (precomposed) Unicode form.

Text pasted from some sources stores accented letters in NFD (decomposed)
form, e.g. "n" + combining tilde (U+0303) instead of the precomposed "ñ"
(U+00F1). Both look identical on screen, but pdflatex chokes on the bare
combining character, failing with "Unicode character ... not set up for
use with LaTeX." This script finds and fixes those cases.

Usage:
    python scripts/normalize_unicode.py         # fix files in place
    python scripts/normalize_unicode.py --check  # report only, exit 1 if any found
"""
import sys
import unicodedata
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


def main():
    check_only = "--check" in sys.argv
    changed = 0

    for path in sorted(CONTENT_DIR.glob("*.md")):
        original = path.read_text(encoding="utf-8")
        normalized = unicodedata.normalize("NFC", original)
        if normalized != original:
            changed += 1
            rel = path.relative_to(CONTENT_DIR.parent)
            if check_only:
                print(f"non-NFC characters found in {rel}")
            else:
                path.write_text(normalized, encoding="utf-8")
                print(f"normalized {rel}")

    if changed == 0:
        print("done: all files already NFC-normalized")
    elif check_only:
        print(f"done: {changed} file(s) need normalization")
        sys.exit(1)
    else:
        print(f"done: {changed} file(s) normalized")


if __name__ == "__main__":
    main()
