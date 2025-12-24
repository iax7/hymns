#!/usr/bin/env python3
"""Standardize the frontmatter of content/*.md to the canonical header.

Canonical keys (plain lowercase ASCII, no accents — see AGENTS.md):

    id, title, autor, compositor, titulo_original, versiculo

The canonical set is what the Hugo templates read (``.Params.autor``,
``.Params.compositor``, ``.Params.versiculo``, ``.Params.titulo_original``).
Hugo lowercases frontmatter keys but keeps accents, so a key like
``Versículo`` becomes ``versículo`` and silently fails to match
``.Params.versiculo``.

This script:
  * strips leading whitespace before the opening ``---`` and trailing
    whitespace on the ``---`` markers (a stray space breaks Hugo's parser),
  * maps every known key variant (``Autor``, ``Autores``, ``Letra``,
    ``Compositor``, ``Compositores``, ``Música``, ``Título en inglés``,
    ``Título original``, ``Título en alemán``, ... , ``Versículo``) to its
    canonical name — in particular every original-title variant (including
    the retired ``titulo_ingles``) collapses into ``titulo_original``,
  * trims surrounding whitespace from every value,
  * quotes values YAML would otherwise misparse (``Salmos: 19:14``),
  * emits the keys in canonical order, leaving unknown keys at the end,
  * leaves the body (everything after the closing ``---``) untouched.

``titulo_original`` holds the hymn's original title in whatever language it
was written (English, Latin, German, Swedish, Spanish, ...). When a file
carried both an English and a non-English original title, both values are
kept, joined by ``; `` with the non-English title first.

Usage:
    python scripts/normalize_frontmatter.py           # fix files in place
    python scripts/normalize_frontmatter.py --check   # report only, exit 1 if any
"""
import re
import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

CANONICAL_ORDER = [
    "id",
    "title",
    "autor",
    "compositor",
    "titulo_original",
    "versiculo",
]

KEY_MAP = {
    "id": "id",
    "title": "title",
    "autor": "autor",
    "autores": "autor",
    "letra": "autor",
    "compositor": "compositor",
    "compositores": "compositor",
    "musica": "compositor",
    "versiculo": "versiculo",
    "titulo_ingles": "titulo_original",
    "titulo_original": "titulo_original",
    "titulo original": "titulo_original",
    "titulo en original": "titulo_original",
    "titulo en aleman": "titulo_original",
    "titulo en latin": "titulo_original",
    "titulo en sueco": "titulo_original",
}

# Keys whose value is in a language other than English; such a value wins over
# an English one when both collapse into `titulo_original`.
ORIGINAL_LANGUAGE_KEYS = {
    "titulo_original",
    "titulo original",
    "titulo en original",
    "titulo en aleman",
    "titulo en latin",
    "titulo en sueco",
}

# Accented/odd spellings that fold onto the ASCII forms above.
KEY_FOLD = {
    "música": "musica",
    "versículo": "versiculo",
    "título en inglés": "titulo_ingles",
    "título en ingles": "titulo_ingles",
    "título original": "titulo original",
    "título en original": "titulo en original",
    "título en alemán": "titulo en aleman",
    "título en latín": "titulo en latin",
    "título en sueco": "titulo en sueco",
}

FRONTMATTER = re.compile(
    r"\A[\s\ufeff]*---[ \t]*\r?\n(?P<fm>.*?)\r?\n---[ \t]*(\r?\n)?",
    re.DOTALL,
)


def fold_key(key: str) -> str:
    k = key.strip().lower()
    return KEY_FOLD.get(k, k)


def scalar(value: str) -> str:
    """Quote a value when YAML would otherwise misparse it."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value  # already a quoted scalar
    needs_quotes = (
        ": " in value
        or value.endswith(":")
        or " #" in value
        or value.startswith("#")
        or (value and value[0] in "!&*?|>%@`[]{},-")
    )
    if needs_quotes:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def canonical_name(key: str) -> str | None:
    return KEY_MAP.get(fold_key(key))


def process(text: str, path: Path | None = None) -> tuple[str, list[str]]:
    """Return (new_text, notes). new_text == text when nothing changed."""
    m = FRONTMATTER.match(text)
    if not m:
        return text, ["no frontmatter found"]

    notes: list[str] = []
    candidates: dict[str, list[tuple[int, int, str]]] = {}
    unknown: list[tuple[str, str]] = []
    seq = 0

    for raw in m.group("fm").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if ":" not in line:
            notes.append(f"dropped non key/value line: {line!r}")
            continue
        key, _, value = line.partition(":")
        canon = canonical_name(key)
        value = value.strip()
        if canon is None:
            unknown.append((key.strip(), value))
            continue
        if not value:
            candidates.setdefault(canon, [])
            continue
        priority = (
            2
            if canon == "titulo_original" and fold_key(key) in ORIGINAL_LANGUAGE_KEYS
            else 1
        )
        candidates.setdefault(canon, []).append((priority, seq, value))
        seq += 1

    values: dict[str, str] = {}
    for canon, cands in candidates.items():
        seen: list[str] = []
        for _, _, v in sorted(cands, key=lambda c: (-c[0], c[1])):
            if v not in seen:
                seen.append(v)
        values[canon] = "; ".join(seen)
        if len(seen) > 1:
            notes.append(f"merged {len(seen)} values into {canon!r}: {values[canon]!r}")

    ordered = [k for k in CANONICAL_ORDER if k in values]
    if "id" not in values:
        notes.append("missing id")
    elif path is not None:
        prefix = re.match(r"(\d+)-", path.name)
        if prefix and values["id"].strip().isdigit() and int(values["id"]) != int(prefix.group(1)):
            notes.append(
                f"id {values['id']!r} does not match filename number {prefix.group(1)!r}"
            )

    lines = ["---"]
    lines += [f"{k}: {scalar(values[k])}".rstrip() for k in ordered]
    lines += [f"{k}: {scalar(v)}".rstrip() for k, v in unknown]
    lines.append("---")

    body = text[m.end():]
    new_text = "\n".join(lines) + "\n" + body
    if unknown:
        notes.append("unknown keys kept: " + ", ".join(k for k, _ in unknown))
    return new_text, notes


def main():
    check_only = "--check" in sys.argv
    changed = 0
    problems = 0

    for path in sorted(CONTENT_DIR.glob("*.md")):
        original = path.read_text(encoding="utf-8")
        updated, notes = process(original, path)
        rel = path.relative_to(CONTENT_DIR.parent)
        if notes:
            problems += 1
            print(f"{rel}: {'; '.join(notes)}")
        if updated != original:
            changed += 1
            if check_only:
                print(f"needs normalization: {rel}")
            else:
                path.write_text(updated, encoding="utf-8")
                print(f"normalized {rel}")

    if check_only:
        if changed:
            print(f"done: {changed} file(s) need normalization")
            sys.exit(1)
        print("done: frontmatter already canonical")
    else:
        print(f"done: {changed} file(s) normalized, {problems} with notes")


if __name__ == "__main__":
    main()
