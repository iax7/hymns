#!/usr/bin/env python3
"""Normalize content/*.md to NFC (precomposed) Unicode form.

Text pasted from some sources stores accented letters in NFD (decomposed)
form, e.g. "n" + combining tilde (U+0303) instead of the precomposed "ñ"
(U+00F1). Both look identical on screen, but pdflatex chokes on the bare
combining character, failing with "Unicode character ... not set up for
use with LaTeX." This script finds and fixes those cases.

Filenames are normalized too: a name pasted from macOS is typically NFD
(`señor`), which git reports as a delete + add pair, so the file looks
duplicated in `git status` and its name no longer matches the tracked one.

Usage:
    python scripts/normalize_unicode.py         # fix files in place
    python scripts/normalize_unicode.py --check  # report only, exit 1 if any found
"""
import sys
import unicodedata
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


def renamed(path: Path) -> Path:
    """NFC form of *path* if the basename is not already NFC."""
    name = unicodedata.normalize("NFC", path.name)
    return path.with_name(name) if name != path.name else path


def main():
    check_only = "--check" in sys.argv
    changed = 0

    for path in sorted(CONTENT_DIR.glob("*.md")):
        rel = path.relative_to(CONTENT_DIR.parent)

        target = renamed(path)
        if target != path:
            changed += 1
            if check_only:
                print(f"non-NFC filename: {rel}")
            elif target.exists():
                print(f"WARNING: cannot rename {rel} -> {target.name} (exists)")
            else:
                path.rename(target)
                print(f"renamed {rel} -> {target.name}")
                path = target

        original = path.read_text(encoding="utf-8")
        normalized = unicodedata.normalize("NFC", original)
        if normalized != original:
            changed += 1
            if check_only:
                print(f"non-NFC characters found in {rel}")
            else:
                path.write_text(normalized, encoding="utf-8")
                print(f"normalized {rel}")

    if changed == 0:
        print("done: all files already NFC-normalized")
    elif check_only:
        print(f"done: {changed} file(s)/name(s) need normalization")
        sys.exit(1)
    else:
        print(f"done: {changed} file(s)/name(s) normalized")


if __name__ == "__main__":
    main()
