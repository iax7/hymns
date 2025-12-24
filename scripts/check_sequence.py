#!/usr/bin/env python3
"""Check that content/*.md is a contiguous sequence with matching ids.

Hymn files are named ``NN-slug.md`` where ``NN`` is the ``id`` frontmatter
field. The ``id`` drives PDF ordering, Hugo URLs, and social image filenames,
so both must line up. This script prints one line per number in ``1..max``
with a check/cross, then reports:

  * gaps — a number in ``1..max`` with no file,
  * mismatches — the frontmatter ``id`` disagrees with the filename number,
  * duplicate ids — two files claiming the same ``id``,
  * files whose name has no leading number.

Usage:
    python scripts/check_sequence.py   # report only, exit 1 if any problem
"""
import re
import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
ID_RE = re.compile(r"^id:\s*(\d+)\s*$", re.MULTILINE)
OK, BAD = "✅", "❌"


def main():
    files = sorted(CONTENT_DIR.glob("*.md"))
    by_number: dict[int, list[Path]] = {}
    extra: list[str] = []

    for path in files:
        prefix = re.match(r"(\d+)-", path.name)
        if not prefix:
            extra.append(f"{path.name}: filename has no leading number")
            continue
        by_number.setdefault(int(prefix.group(1)), []).append(path)

    notes: dict[int, list[str]] = {}
    id_owner: dict[int, str] = {}

    for num, paths in by_number.items():
        bucket = notes.setdefault(num, [])
        if len(paths) > 1:
            bucket.append(f"filename number {num} used by {len(paths)} files")
        for path in paths:
            m = ID_RE.search(path.read_text(encoding="utf-8"))
            if not m:
                bucket.append(f"{path.name}: missing or non-numeric 'id'")
                continue
            file_id = int(m.group(1))
            if file_id != num:
                bucket.append(f"{path.name}: id {file_id} != filename number {num}")
            if file_id in id_owner:
                bucket.append(f"{path.name}: id {file_id} already used by {id_owner[file_id]}")
            else:
                id_owner[file_id] = path.name

    maxnum = max(by_number, default=0)
    width = max(len(str(maxnum)), 3)

    for n in range(1, maxnum + 1):
        bucket = notes.get(n)
        if bucket is None:
            print(f"{n:>{width}} -> {BAD}  missing file")
        elif bucket:
            print(f"{n:>{width}} -> {BAD}  {'; '.join(bucket)}")
        else:
            print(f"{n:>{width}} -> {OK}")

    for line in extra:
        print(f"{'':>{width}} -> {BAD}  {line}")

    problems = sum(len(b) for b in notes.values()) + len(extra)
    if maxnum == 0:
        print("done: no content found")
        sys.exit(1)
    if problems:
        print(f"done: {problems} problem(s) in sequence 1..{maxnum}")
        sys.exit(1)
    print(f"done: {len(files)} file(s), sequence 1..{maxnum} intact")


if __name__ == "__main__":
    main()
