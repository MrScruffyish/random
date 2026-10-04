#!/usr/bin/env bash

# ============================================================
# A4 -> A3 book imposition using pdfimpose 2.9.0
#
# Default:
#   16-page signatures
#   A4 source pages
#   A3 landscape output
#   2 A4 pages per A3 sheet
#   no scaling
#
# Usage:
#
#   ./booklet.sh guide.pdf
#
#   ./booklet.sh guide.pdf 16
#
#   ./booklet.sh guide.pdf 32
#
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Arguments
# ------------------------------------------------------------

INPUT="${1:-guide.pdf}"
SIGNATURE="${2:-16}"

if [[ ! -f "$INPUT" ]]; then
    echo "Error: input file does not exist:"
    echo "  $INPUT"
    exit 1
fi

# ------------------------------------------------------------
# Check signature size
# ------------------------------------------------------------

if ! [[ "$SIGNATURE" =~ ^[0-9]+$ ]]; then
    echo "Error: signature size must be an integer."
    exit 1
fi

if (( SIGNATURE < 4 || SIGNATURE % 4 != 0 )); then
    echo "Error: signature size must be a multiple of 4."
    exit 1
fi

# Number of printed A3 sheets in one signature.
SHEETS=$((SIGNATURE / 4))

# ------------------------------------------------------------
# Check pdfimpose
# ------------------------------------------------------------

if ! command -v pdfimpose >/dev/null 2>&1; then
    echo "Error: pdfimpose is not installed."
    echo
    echo "Install version 2.9.0 with:"
    echo
    echo "    python3 -m pip install pdfimpose==2.9.0"
    echo
    exit 1
fi

# ------------------------------------------------------------
# Check version
# ------------------------------------------------------------

VERSION=$(pdfimpose --version 2>/dev/null || true)

if [[ -n "$VERSION" ]]; then
    echo "pdfimpose: $VERSION"
fi

# ------------------------------------------------------------
# Output filename
# ------------------------------------------------------------

BASENAME="${INPUT%.pdf}"
OUTPUT="${BASENAME}-A3-${SIGNATURE}page-signatures.pdf"

# ------------------------------------------------------------
# Information
# ------------------------------------------------------------

echo
echo "Input PDF:          $INPUT"
echo "Signature:          $SIGNATURE pages"
echo "A3 sheets/signature: $SHEETS"
echo "Layout:             2 x 1 A4 pages"
echo "Output:             $OUTPUT"
echo
echo "No input-page scaling will be requested."
echo

# ------------------------------------------------------------
# Imposition
# ------------------------------------------------------------
#
# hardcover:
#   intended for real books where sheets are individually
#   folded, stacked, and bound.
#
# --signature 2x1:
#   two A4 pages across one sheet.
#
#   2 * 210 mm = 420 mm
#   1 * 297 mm = 297 mm
#
#   => A3 landscape.
#
# --group N:
#   group N printed sheets into one signature.
#
# For a 16-page signature:
#
#       16 pages / 4 pages per sheet = 4 sheets
#
# Therefore:
#
#       --group 4
#
# --imargin 0:
#   no additional margin around input pages.
#
# --omargin 0:
#   no additional margin around output pages.
#
# --bind left:
#   book binds on the left.
#
# ------------------------------------------------------------

pdfimpose hardcover \
    --signature 2x1 \
    --group "$SHEETS" \
    --bind left \
    --imargin 0 \
    --omargin 0 \
    --output "$OUTPUT" \
    "$INPUT"

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------

echo
echo "Finished:"
echo
echo "    $OUTPUT"
echo
echo "Each signature contains:"
echo "    $SIGNATURE A4 pages"
echo "    $SHEETS A3 sheets"
echo
echo "Print the resulting PDF:"
echo "    Paper:       A3"
echo "    Orientation: Landscape"
echo "    Scaling:     100% / Actual size"
echo "    Duplex:      Yes"
echo "    Binding:     Left"
echo
