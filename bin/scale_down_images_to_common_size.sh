#!/usr/bin/env bash
# Scale down to smallest common size keeping aspect ratio, and pad with white if needed.
# Best used on a set of images with approximatly the same size.

set -euo pipefail

if (( $# < 2 )); then
    echo "Usage: $0 image1 image2 [image3 ...]"
    exit 1
fi

# Detect ImageMagick
if command -v magick >/dev/null 2>&1; then
    IM_IDENTIFY=(magick identify)
    IM_CONVERT=(magick)
    echo "Using ImageMagick 7"
elif command -v identify >/dev/null 2>&1 && \
     command -v convert >/dev/null 2>&1; then
    IM_IDENTIFY=(identify)
    IM_CONVERT=(convert)
    echo "Using ImageMagick 6"
else
    echo "Error: ImageMagick not found."
    exit 1
fi

# Find smallest dimensions
min_width=999999
min_height=999999
valid_images=()

echo "Examining images..."

for img in "$@"; do
    if [[ ! -f "$img" ]]; then
        echo "Skipping: $img (not found)"
        continue
    fi

    if ! dimensions=$("${IM_IDENTIFY[@]}" -format '%w %h' "$img"); then
        echo "Skipping: $img (cannot identify)"
        continue
    fi

    read -r w h <<< "$dimensions"

    echo "  $img: ${w}x${h}"

    valid_images+=("$img")

    if (( w < min_width )); then
        min_width=$w
    fi

    if (( h < min_height )); then
        min_height=$h
    fi
done

if (( ${#valid_images[@]} == 0 )); then
    echo "Error: No valid images found."
    exit 1
fi

echo
echo "Target canvas: ${min_width}x${min_height}"
echo

# Process images
for img in "${valid_images[@]}"; do
    filename="${img%.*}"
    extension="${img##*.}"
    output="${filename}_scaled.${extension}"

    echo "Processing: $img -> $output"

    "${IM_CONVERT[@]}" "$img" \
        -resize "${min_width}x${min_height}" \
        -background white \
        -gravity center \
        -extent "${min_width}x${min_height}" \
        "$output"
done

echo
echo "Done!"
