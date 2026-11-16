# `skapa_pdf_from_many_images.py`

Creates a printable PDF by placing all PNG images from a directory into a fixed `rows × cols` grid per page. Images are sorted alphabetically by filename (case-insensitive), scaled to a uniform target size in millimetres, and annotated with corner cut/crop marks.

## Requirements

- Python 3
- [Pillow](https://python-pillow.org/)
- [ReportLab](https://www.reportlab.com/dev/opensource/)

Install (example):

```bash
python3 -m pip install pillow reportlab
```

## Usage

```bash
./bin/skapa_pdf_from_many_images.py --papersize {a3|a4} --rows N --cols N --width-mm W --height-mm H [options]
```

### Required arguments

- `-p, --papersize` — `a3` or `a4`
- `-r, --rows` — rows per page (>= 1)
- `-c, --cols` — columns per page (>= 1)
- `-w, --width-mm` — target image width in mm (> 0)
- `-H, --height-mm` — target image height in mm (> 0)

### Common options

- `-o, --output` — output PDF filename (default: `printable_output.pdf`)
- `-d, --directory` — directory to scan for `*.png` (default: current directory; non-recursive)
- `-O, --orientation` — `portrait` (default) or `landscape`
- `--stretch` — force each image to fill the target box exactly, distorting aspect ratio if needed
  - default behavior preserves aspect ratio and fits/centers image inside the target box
- `--margin-mm` — margin on all edges in mm (default: `10.0`), unless overridden
- `--margin-long-mm` / `--margin-short-mm` — margins relative to the physical page's long/short edge pairs (override `--margin-mm` for those edges)
- `--mark-length` — crop mark leg length in points (default: `10.0`)
- `--mark-gap` — gap from target box edge to mark start in points (default: `3.0`)

### Examples

```bash
# A4 portrait, 2x3 grid, 50x50 mm images
./bin/skapa_pdf_from_many_images.py -p a4 -r 2 -c 3 -w 50 -H 50

# A3 landscape with custom output
./bin/skapa_pdf_from_many_images.py -p a3 -r 3 -c 3 -w 70 -H 40 -O landscape -o output.pdf

# Stretch images to fill target box, read PNGs from ./scans
./bin/skapa_pdf_from_many_images.py -p a4 -r 2 -c 2 -w 60 -H 60 --stretch -d ./scans

# Different margins on long/short page edges
./bin/skapa_pdf_from_many_images.py -p a4 -r 2 -c 3 -w 40 -H 40 --margin-long-mm 20 --margin-short-mm 10
```

## Behavior and layout rules

- **Input:** all `*.png` files directly inside `--directory`, sorted by filename (case-insensitive).
- **Uniform sizing:** every image is scaled to the same target box (`--width-mm × --height-mm`).
- **Crop marks:** drawn at the corners of the **target box** (not the possibly smaller fitted image), forming a consistent trim grid.
- **Validation:** the script fails with an error if the target box does not fit into the grid cells given paper size, orientation, and margins. Adjust size, margins, rows/cols, or paper size to fix.
- **Pagination:** pages are added as needed to fit all images (`rows × cols` slots per page).
