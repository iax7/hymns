# Hymns Project Justfile
# Common tasks for building PDF and generating social images

set shell := ["zsh", "-cu"]

# Default recipe
default:
    @just --list

# Check content/*.md for non-NFC Unicode (fails the PDF build otherwise)
[group('pdf')]
check-unicode:
    python3 scripts/normalize_unicode.py --check

# Normalize content/*.md to NFC Unicode (also renames non-NFC filenames)
[group('pdf')]
fix-unicode:
    python3 scripts/normalize_unicode.py

# Check content/*.md frontmatter for non-canonical keys
[group('content')]
check-frontmatter:
    python3 scripts/normalize_frontmatter.py --check

# Rewrite content/*.md frontmatter to the canonical keys and order
[group('content')]
fix-frontmatter:
    python3 scripts/normalize_frontmatter.py

# Restore the two-space markdown hard breaks in content/*.md bodies
[group('content')]
fix-lines:
    python3 scripts/add_line_breaks.py

# Check content/*.md numbering is contiguous and frontmatter id matches filename
[group('content')]
check-sequence:
    python3 scripts/check_sequence.py

# Build PDF hymnal
[group('pdf')]
pdf: check-unicode
    scripts/build-pdf.sh

# Build PDF hymnal in a container. Usage: just pdf-docker [engine] (default: docker)
[group('pdf')]
pdf-docker engine='docker':
    {{ engine }} build -t hymns-pdf .
    {{ engine }} run --rm -v "$(pwd)":/data hymns-pdf

# Generate social image for a single hymn

# Generate an image. Usage: just image <hymn_id>
[group('web')]
image hymn_id:
    python scripts/generate_image.py {{ hymn_id }}

# Default: 100 hymns
[group('web')]
images number='100':
    ./scripts/generate_all_images.sh {{ number }}

# Development server preview
[group('dev')]
serve:
    hugo server -D

# Production build
build:
    hugo --minify
