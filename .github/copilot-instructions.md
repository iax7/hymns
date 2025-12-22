# Hymns Project Guidelines

Spanish hymnal built with Hugo static site generator. Dual output: website deployed to GitHub Pages and PDF via Pandoc.

## Content Conventions

**Hymn Files** (`content/*.md`):

- Naming: `NN-hymn-slug.md` where NN is zero-padded ID (e.g., `01-oh-gran-dios.md`)
- Required frontmatter fields (YAML):
  - `id`: Numeric identifier (critical for sorting, URLs, social images)
  - `Title`: Spanish hymn title
  - `Autor`: Author name(s)
  - `Compositor`: Composer name(s)
  - `Título en inglés`: Original English title
  - `Versículo`: Biblical reference (e.g., "2 Corintios 4:6")
- Body: Plain text stanzas separated by blank lines, no special chorus markup
- Language: Spanish lyrics with English metadata

## Build Commands

**Development**:

```bash
hugo server -D
```

Local preview at `http://localhost:1313/`

**Production**:

```bash
hugo --minify
```

Outputs to `public/` directory

**PDF Generation**:

```bash
./build-pdf.sh
```

Requires: Pandoc, BasicTeX, LaTeX packages (titlesec, fancyhdr, parskip, ebgaramond, gillius)

**Social Images** (scripts in `scripts/` folder):

```bash
python scripts/generate_image.py <hymn_id>         # Single hymn
./scripts/generate_all_images.sh <number_of_hymns> # Batch generation
```

## Architecture

- **Hugo site**: Static generator with custom layouts
- **Layouts**: Responsive design with theme toggle, search, Wake Lock API
- **PDF build**: Shell script aggregates hymns by ID, uses Pandoc with custom LaTeX template
- **Typography**: Libre Baskerville (hymn text), Inter (UI), EB Garamond (PDF)
- **Deployment**: GitHub Pages via `public/` folder

## Key Patterns

- **ID is critical**: Hymn `id` field drives sorting, PDF order, URL structure, and social image mapping
- **Theme support**: Light/dark mode with system preference detection and localStorage
- **Search**: Client-side filtering with normalized text matching (accent/punctuation insensitive)
- **Social previews**: Per-hymn Open Graph images (`hymn-NNN.jpg`) in `static/images/`
- **No automation**: PDF generation and image creation are manual processes

## Common Tasks

- **Add new hymn**: Create `content/NN-slug.md` with all required frontmatter, generate social image
- **Update hymn**: Preserve frontmatter structure, maintain stanza separation
- **Modify layouts**: Check `layouts/_default/` for template logic (baseof, single, list)
- **Style changes**: Edit `static/css/style.css` (uses CSS custom properties for theming)

## Code Style

- **All code and comments must be in English**, including shell scripts, configuration files, and any generated code
- Use clear, descriptive variable and function names in English
- Include English-language comments explaining non-obvious logic
