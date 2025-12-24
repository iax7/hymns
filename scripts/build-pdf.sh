#!/bin/bash
set -e  # Exit on error

# Output file
OUTPUT="himnario.pdf"
TEMP_MD="himnario-full.md"

# Cleanup on exit (success or failure)
trap 'rm -f "$TEMP_MD"' EXIT

# Verify dependencies
command -v pandoc >/dev/null 2>&1 || { echo "Error: pandoc is not installed"; exit 1; }
command -v pdflatex >/dev/null 2>&1 || { echo "Error: pdflatex is not installed"; exit 1; }

# Verify required directories and files
[[ -d "content" ]] || { echo "Error: content/ directory does not exist"; exit 1; }
[[ -f "templates/pdf.tex" ]] || { echo "Error: templates/pdf.tex does not exist"; exit 1; }

# Clear temp file
> "$TEMP_MD"

echo "Building $OUTPUT..."

# 1. Iterate files sorted by numeric ID
# grep recursive for id, extract file and id, sort by id, process
hymn_count=0
while read -r filename id; do
    FULL_PATH="content/$filename.md"

    # Verify file exists
    if [[ ! -f "$FULL_PATH" ]]; then
        echo "Warning: $FULL_PATH not found, skipping..."
        continue
    fi

    # Extract metadata
    TITLE=$(grep "^Title:" "$FULL_PATH" | head -n 1 | cut -d: -f2- | sed 's/^ *//;s/^"//;s/"$//')

    if [[ -z "$TITLE" ]]; then
        echo "Warning: Hymn $id without title in $FULL_PATH"
        TITLE="Untitled"
    fi

    # Format Header for the Hymn
    echo "# $id. $TITLE" >> "$TEMP_MD"

    # Extract Body:
    # Remove front matter (everything between first --- and second ---)
    awk '/^---$/{if(++count==2) next; if(count>=1) next} count>=2' "$FULL_PATH" >> "$TEMP_MD"

    # Add page break
    echo "" >> "$TEMP_MD"
    echo "\\newpage" >> "$TEMP_MD"
    echo "" >> "$TEMP_MD"

    ((hymn_count++))
done < <(grep -H "^id:" content/*.md | sed 's/content\///' | sed 's/\.md:id: / /' | sort -n -k 2)

echo "Processed $hymn_count hymns"

# 2. Run Pandoc
echo "Generating PDF with Pandoc..."
if pandoc "$TEMP_MD" \
    -o "$OUTPUT" \
    --template=templates/pdf.tex \
    --pdf-engine=pdflatex \
    -V geometry:letterpaper \
    -V geometry:margin=1.5cm; then
    echo "✓ PDF created successfully: $OUTPUT"
else
    echo "✗ Error generating PDF"
    exit 1
fi
