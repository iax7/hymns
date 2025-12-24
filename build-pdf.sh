#!/bin/bash

# Output file
OUTPUT="himnario.pdf"
TEMP_MD="himnario-full.md"

# Clear temp file
echo "" > "$TEMP_MD"

echo "Building $OUTPUT..."

# 1. Iterate files sorted by numeric ID
# grep recursive for id, extract file and id, sort by id, process
grep -H "^id:" content/*.md | sed 's/content\///' | sed 's/\.md:id: / /' | sort -n -k 2 | while read -r filename id; do
    FULL_PATH="content/$filename.md"

    # Extract metadata
    TITLE=$(grep "^Title:" "$FULL_PATH" | head -n 1 | cut -d: -f2- | sed 's/^ *//;s/^"//;s/"$//')

    # Format Header for the Hymn
    echo "# $id. $TITLE" >> "$TEMP_MD"

    # Extract Body:
    # 1. remove front matter (sed 1,/^---$/d)
    cat "$FULL_PATH" | sed '1,/^---$/d' >> "$TEMP_MD"

    # Add page break
    echo "" >> "$TEMP_MD"
    echo "\newpage" >> "$TEMP_MD"
    echo "" >> "$TEMP_MD"
done

# 2. Run Pandoc
pandoc "$TEMP_MD" \
    -o "$OUTPUT" \
    --template=templates/pdf.tex \
    --pdf-engine=pdflatex \
    -V geometry:letterpaper \
    -V geometry:margin=1.5cm

# Cleanup
rm "$TEMP_MD"

echo "PDF: $OUTPUT"
