#!/bin/bash

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 input.txt output.png"
    exit 1
fi

# Escape special characters for Pango
TEXT=$(sed -e 's/&/\&amp;/g' \
           -e 's/</\&lt;/g' \
           -e 's/>/\&gt;/g' "$INPUT")

convert -background white \
        -fill black \
        -font "Courier" \
        -pointsize 18 \
        pango:"<tt>$TEXT</tt>" \
        "$OUTPUT"

echo "Saved to $OUTPUT"