---
name: tune-pdf-pagination
description: Tune the LONG_HYMN_THRESHOLD used by scripts/build-pdf.sh to decide page breaks between hymns in the PDF. Use when the PDF output has awkward page breaks, orphaned titles, or a hymn split badly across columns/pages, or when the user asks to retune pagination after editing hymn content.
---

Rebuild the PDF (`just pdf`) and inspect `himnario.pdf` for pagination problems: a hymn title orphaned at the bottom of a column, a hymn splitting awkwardly across a page boundary, or a long hymn bleeding past a page in a way that looks wrong.

To diagnose, run `scripts/list-hymns.py [threshold]` (default threshold matches `LONG_HYMN_THRESHOLD` in `scripts/build-pdf.sh`, currently 44). It prints each hymn's rendered line count (wide lines that wrap in the two-column layout count as 2+ lines, measured against real EB Garamond font metrics) and whether it's classified SHORT or LONG. Hymns near the threshold boundary are the likely cause of bad breaks.

To fix:
1. Identify which hymn(s) are misclassified relative to how they actually render (e.g. a hymn just under the threshold that still doesn't fit cleanly in a column).
2. Adjust `LONG_HYMN_THRESHOLD` in `scripts/build-pdf.sh` (and pass the same value to `scripts/list-hymns.py` to verify the new classification matches expectations).
3. Rebuild with `just pdf` and re-check the rendered PDF around the affected hymn(s).
4. Iterate — this is a manually-tuned magic number, not something to solve analytically. Small threshold changes can reclassify several hymns at once, so re-check the whole document, not just the hymn you were fixing.

Don't touch the `\titleformat{\section}` pagebreak logic in `templates/pdf.tex` unless the problem is specifically a section title (hymn heading) being orphaned at the bottom of a column — that's a separate, already-tuned concern from the newpage/clearpage logic in `build-pdf.sh`.
