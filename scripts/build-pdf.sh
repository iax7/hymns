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

# Long hymn threshold: hymns with more body lines than this may overflow one
# column. Only these get special treatment to avoid crossing a page boundary.
# A long hymn starting at col1 can safely overflow into col2 of the same page.
# A long hymn starting at col2 would overflow to col1 of the NEXT page (bad),
# so we use \clearpage to force it back to col1 of a fresh page.
LONG_HYMN_THRESHOLD=44

# 1. Iterate files sorted by numeric ID
# grep recursive for id, extract file and id, sort by id, process
hymn_count=0
prev_col=0      # Column the previous hymn started in (0=col1, 1=col2)
prev_was_long=0 # Whether the previous hymn may have overflowed its column

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

    # Count body lines (text + blank) to decide break type for this hymn
    body_lines=$(awk '/^---$/{if(++count==2){found=1;next}} found' "$FULL_PATH" | wc -l)
    is_long=0
    [[ $body_lines -gt $LONG_HYMN_THRESHOLD ]] && is_long=1

    if [[ $hymn_count -gt 0 ]]; then
        # Determine which column a \newpage would land at given where the
        # previous hymn ended:
        #   - Short hymn at col1 → \newpage → col2 (=1)
        #   - Short hymn at col2 → \newpage → col1 of next page (=0)
        #   - Long hymn at col1 overflows to col2 → \newpage → col1 (=0)
        if [[ $prev_col -eq 1 || $prev_was_long -eq 1 ]]; then
            newpage_col=0
        else
            newpage_col=1
        fi

        echo "" >> "$TEMP_MD"
        if [[ $is_long -eq 1 && $newpage_col -eq 1 ]]; then
            # Long hymn would land at col2: force col1 of a fresh page instead
            echo "\\clearpage" >> "$TEMP_MD"
            cur_col=0
        else
            echo "\\newpage" >> "$TEMP_MD"
            cur_col=$newpage_col
        fi
        echo "" >> "$TEMP_MD"
    else
        cur_col=0  # First hymn always starts at col1
    fi

    # Format Header for the Hymn
    echo "# $id. $TITLE" >> "$TEMP_MD"

    # Extract Body:
    # Remove front matter (everything between first --- and second ---)
    awk '/^---$/{if(++count==2) next; if(count>=1) next} count>=2' "$FULL_PATH" >> "$TEMP_MD"

    prev_col=$cur_col
    prev_was_long=$is_long
    hymn_count=$((hymn_count + 1))
done < <(grep -H "^id:" content/*.md | sed 's/content\///' | sed 's/\.md:id: / /' | sort -n -k 2)

echo "Processed $hymn_count hymns"

# 2. Run Pandoc
echo "Generating PDF with Pandoc..."
if pandoc "$TEMP_MD" \
    -o "$OUTPUT" \
    --template=templates/pdf.tex \
    --pdf-engine=pdflatex \
    -V geometry:letterpaper \
    -V geometry:margin=1cm; then
    echo "✓ PDF created successfully: $OUTPUT"
else
    echo "✗ Error generating PDF"
    exit 1
fi
