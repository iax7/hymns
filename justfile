# Hymns Project Justfile
# Common tasks for building PDF and generating social images

set shell := ["zsh", "-cu"]

# Default recipe
default:
    @just --list

# Build PDF hymnal
[group('pdf')]
pdf:
    scripts/build-pdf.sh

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
