# Agents.md

This file provides guidance to agents working in this repository.

## Project

Spanish-language hymnal (Himnario de la Gracia) with two outputs: a Hugo static site deployed to GitHub Pages, and a PDF booklet built with Pandoc + LaTeX.

## Content conventions

Hymn files live in `content/*.md`:

- Naming: `NN-hymn-slug.md`, where `NN` is the `id` (zero-padded below 100, e.g. `01-oh-gran-dios.md`). The slug is plain ASCII — strip accents (`señor` → `senor`, `niño` → `nino`), because the filename is the URL: Hugo percent-encodes non-ASCII, so `58-oh-criaturas-del-señor.md` ships as `/58-oh-criaturas-del-se%C3%B1or/`.
- Frontmatter fields (plain lowercase keys, no accents, to avoid Hugo's key-lowercasing ambiguity):
  - `id`: numeric identifier — drives sorting, URLs, PDF order, and social image filenames.
  - `title`: Spanish hymn title (Hugo's standard field; Hugo lowercases frontmatter keys anyway, so keep it lowercase like every other key).
  - `autor`: author name(s).
  - `compositor`: composer name(s).
  - `titulo_original`: the hymn's original title in whatever language it was written (English, Latin, German, Swedish, Spanish…), optional. This is the single original-title field — the retired `titulo_ingles` was merged into it. `scripts/normalize_frontmatter.py` folds every variant (`Título en inglés`, `Título en alemán`, `Título en latín`, `Título en Sueco`, `Título original`) into it; when a file carried two, the values are kept joined by `; `, non-English first.
  - `versiculo`: biblical reference (e.g. `2 Corintios 4:6`).
- Body: plain text stanzas separated by blank lines, no special chorus markup. Every non-blank lyric line ends with exactly two trailing spaces (Markdown hard line break); `.editorconfig` disables trailing-whitespace trimming for `*.md`, so do not strip them. `scripts/add_line_breaks.py` restores them if lost.
- Language: Spanish lyrics, with metadata fields in Spanish keys but English-language values where applicable (author/title).

## Build commands

Task runner is `just` (not npm/make):

Recipes (justfile uses `set shell := ["zsh", "-cu"]`):

```bash
just serve            # hugo server -D, preview at http://localhost:1313/
just build             # hugo --minify, outputs to public/
just check-frontmatter # fails if any content/*.md header is not on canonical keys
just fix-frontmatter   # rewrite content/*.md headers to canonical keys/order
just check-unicode     # fails if content/*.md has non-NFC Unicode (see Gotchas)
just fix-unicode       # normalize content/*.md to NFC in place (also renames NFD filenames)
just pdf               # check-unicode then scripts/build-pdf.sh -> himnario.pdf at repo root
just image <hymn_id>   # python scripts/generate_image.py <id>
just images [number]   # scripts/generate_all_images.sh, default 100
```

Requires (see README.md for install commands): `hugo`, `pandoc`, `pdflatex` (BasicTeX + `tlmgr install titlesec fancyhdr parskip etoolbox ebgaramond gillius extsizes fontaxes`), `python3` + Pillow, `just`.

`just pdf` needs pandoc/pdflatex installed on the host, including `sudo tlmgr install ...`. To avoid installing those as root locally, use `just pdf-docker` instead — it builds `Dockerfile` (based on `pandoc/latex`, with the required LaTeX packages installed inside the container) and runs `scripts/build-pdf.sh` against a mounted copy of the repo.

There is no test suite, linter, or CI validation of hymn content — CI (`.github/workflows/hugo.yml`) only builds and deploys the Hugo site on push to `master`, using a pinned Hugo version (`hugo-version` in that workflow — bump deliberately, don't track `latest`).

## Architecture

- **Hugo site**: static generator with custom layouts in `layouts/_default/` (`baseof.html`, `single.html`, `list.html`) and `layouts/partials/social-meta.html`. `layouts/404.html` provides a branded 404 page for GitHub Pages.
- **PDF build**: `scripts/build-pdf.sh` aggregates hymns by `id`, uses Pandoc with a custom LaTeX template.
- **Typography**: Libre Baskerville (hymn text), Inter (UI), EB Garamond (PDF).
- **Deployment**: GitHub Pages, built from the `public/` folder by CI.

## Key patterns

- **Theme support**: light/dark mode in `baseof.html`, with system-preference detection and a `localStorage` toggle.
- **Font-size control**: `single.html` lets readers resize hymn text (`adjustFontSize`); the chosen size persists via `localStorage` the same way theme does.
- **Search**: client-side filtering in `list.html`, with accent/punctuation-insensitive normalized matching (`normalize('NFD')` + strip diacritics).
- **Social previews**: per-hymn Open Graph images (`hymn-{id:03d}.jpg`) in `static/images/`, wired up in `social-meta.html`.
- **Wake Lock**: `single.html` requests the Screen Wake Lock API so the screen doesn't sleep mid-hymn (useful for live singing).
- **No automation**: PDF generation and social image creation are manual, not part of CI.

## PDF pagination tuning

`scripts/build-pdf.sh` decides between `\newpage` and `\clearpage` between hymns based on `LONG_HYMN_THRESHOLD` (currently 44 body lines), to avoid awkward page breaks in the two-column layout. `scripts/list-hymns.py [threshold]` prints a table of every hymn's rendered line count (accounting for lines that wrap in the two-column layout, measured against the actual EB Garamond font metrics) and short/long classification — use it when tuning the threshold after content changes, rather than guessing.

## Common tasks

- **Add new hymn**: create `content/NN-slug.md` with the frontmatter fields above, then generate its social image (`just image <id>`).
- **Update hymn**: preserve frontmatter structure, maintain stanza separation.
- **Modify layouts**: templates live in `layouts/_default/` (`baseof`, `single`, `list`) and `layouts/partials/`.
- **Style changes**: edit `static/css/style.css` (uses CSS custom properties for theming).

## Gotchas

- The `id` frontmatter field on each hymn drives PDF ordering, Hugo URLs, and social image filenames (`hymn-{id:03d}.jpg`) — it must be unique and match the filename number. Past batches shipped duplicates (two files claiming `id: 109`, `149`/`145`, `171`/`170`) and off-by-one ids; `just fix-frontmatter` reports any file whose `id` disagrees with its filename number, but it does not renumber silently. `build-pdf.sh` sorts by the frontmatter `id`, not the filename, so verify with `grep -h '^id:' content/*.md | sort | uniq -d` before adding or renumbering.
- Content must be NFC-normalized Unicode. Accents pasted in NFD (decomposed) form look identical but make pdflatex fail with "Unicode character ... not set up for use with LaTeX." `just pdf` runs `just check-unicode` first; run `just fix-unicode` to repair. This applies to **filenames too** — a batch copied from macOS keeps NFD names, which git reports as delete + add pairs; `fix-unicode` renames those as well.
- A re-sent batch of hymns typically arrives with capitalized/accented frontmatter keys (`Autor`, `Título en inglés`, `Versículo`), stripped two-space line breaks, and sometimes a space before the opening `---`. Repair headers with `just fix-frontmatter` and line breaks with `just fix-lines` before committing.
- Hugo lowercases frontmatter keys but preserves accents — a key like `Título en inglés` and `Titulo en ingles` are two different params. Stick to plain ASCII lowercase keys (see Content conventions above) to avoid silently-unmatched lookups in templates.
- `generate_image.py` hardcodes macOS font paths (`/System/Library/Fonts/Supplemental/...`) and silently falls back to a low-quality default font on other platforms — don't assume image output quality when running elsewhere.
- PDF and image generation are manual, not part of CI — after adding or editing a hymn, remember to regenerate the PDF and social image if needed.
