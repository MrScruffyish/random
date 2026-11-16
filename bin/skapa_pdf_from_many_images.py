#!/usr/bin/env python3
"""
generate_printable_pdf_from_images.py

Places every PNG image found in a folder onto a printable PDF, arranged in
a grid of `rows` x `cols` images per page, sorted by filename. Every image
is scaled to the SAME physical size, given in millimetres (--width-mm /
--height-mm). Each placed image gets small cut/crop marks in its four
corners so you can trim the printed sheet with a knife or scissors -- since
every image is forced to the same target size, the marks line up into a
clean, uniform trim grid across the whole page.

Usage:
    python3 generate_printable_pdf_from_images.py --papersize a4 --rows 2 --cols 3 --width-mm 50 --height-mm 50
    python3 generate_printable_pdf_from_images.py -p a3 -r 3 -c 3 -w 70 -H 40 -o output.pdf
    python3 generate_printable_pdf_from_images.py -p a4 -r 2 -c 2 -w 60 -H 60 --orientation landscape
    python3 generate_printable_pdf_from_images.py -p a4 -r 2 -c 2 -w 60 -H 60 --stretch
    python3 generate_printable_pdf_from_images.py -p a4 -r 2 -c 3 -w 40 -H 40 --directory ./scans
    python3 generate_printable_pdf_from_images.py -p a4 -r 2 -c 3 -w 40 -H 40 --margin-mm 15
    python3 generate_printable_pdf_from_images.py -p a4 -r 2 -c 3 -w 40 -H 40 --margin-long-mm 20 --margin-short-mm 10

    Paper orientation defaults to portrait. Use --orientation landscape (or
    -O landscape) to rotate the page.

Notes on sizing:
    Every image is scaled down (or up) to fit within a --width-mm x
    --height-mm box, so all printed images end up exactly the same size.
    By default the image's aspect ratio is preserved (it's fitted inside
    the box and centered, so it may not fill the box completely on one
    axis). Pass --stretch to instead force the image to fill the box
    exactly on both axes, distorting the aspect ratio if needed.

    Cut marks are always drawn at the corners of the target box itself
    (not the possibly-smaller scaled image), so every cut mark on the page
    is the same size and forms a uniform grid, regardless of each source
    image's original aspect ratio.

    If the target box (plus margins) doesn't fit into the rows x cols
    grid, the script FAILS with an error instead of silently overflowing
    images into neighboring cells. Shrink --width-mm/--height-mm, reduce
    margins, reduce rows/cols, or pick a bigger paper size instead.

Notes on margins:
    Margins are given in millimetres and measured from the paper edge in
    on that axis. Use a single --margin-mm for the same margin all around,
    or set --margin-long-mm and --margin-short-mm separately:
      - "long-edge margin" is the margin along the pair of page edges that
        run the LONG way (e.g. left/right margins on a portrait page).
      - "short-edge margin" is the margin along the pair of page edges
        that run the SHORT way (e.g. top/bottom margins on a portrait
        page).
    These are defined relative to the physical page dimensions (after
    orientation is applied), so e.g. --margin-long-mm always refers to the
    margin next to the paper's longer sides, in both portrait and
    landscape. --margin-long-mm / --margin-short-mm, if given, override
    --margin-mm for that edge pair.

Notes on input files:
    All *.png files directly inside --directory (default: current folder)
    are used, sorted alphabetically by filename (case-insensitive).
"""

import argparse
import glob
import os
import sys

from PIL import Image
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


PAPER_SIZES = {
    "a3": A3,
    "a4": A4,
}

DEFAULT_MARGIN_MM = 10.0
DEFAULT_MARK_LENGTH_PT = 10.0
DEFAULT_MARK_GAP_PT = 3.0
DEFAULT_MARK_LINE_WIDTH_PT = 0.5


class LayoutError(Exception):
    """Raised when the requested layout cannot fit on the page."""


def find_png_files(directory="."):
    """Return a sorted (by filename, case-insensitive) list of all .png
    files directly inside `directory`."""
    files = sorted(
        glob.glob(os.path.join(directory, "*.png")),
        key=lambda p: os.path.basename(p).lower(),
    )
    return files


def get_draw_size_pt(path, target_w_pt, target_h_pt, stretch):
    """
    Return (draw_width_pt, draw_height_pt) for the image at `path` when
    scaled to the target box (target_w_pt x target_h_pt).

    If `stretch` is False (default), the image is scaled uniformly so it
    fits entirely within the target box, preserving its aspect ratio
    (letterboxed/centered if the aspect ratio doesn't match).

    If `stretch` is True, the image is scaled independently on each axis
    to exactly fill the target box, which may distort its aspect ratio.
    """
    if stretch:
        return target_w_pt, target_h_pt

    with Image.open(path) as im:
        px_w, px_h = im.size

    scale = min(target_w_pt / px_w, target_h_pt / px_h)
    return px_w * scale, px_h * scale


def resolve_margins_pt(page_width, page_height, margin_mm, margin_long_mm, margin_short_mm):
    """
    Resolve horizontal/vertical margins (in points) from the user's
    mm settings and the actual (post-orientation) page dimensions.

    "long-edge margin" applies next to the pair of edges that run along
    the page's LONGER dimension (left/right edges on a portrait page,
    top/bottom edges on a landscape page).
    "short-edge margin" applies next to the other pair of edges.
    """
    long_mm = margin_long_mm if margin_long_mm is not None else margin_mm
    short_mm = margin_short_mm if margin_short_mm is not None else margin_mm
    long_pt = long_mm * mm
    short_pt = short_mm * mm

    if page_height >= page_width:
        # Portrait-like: left/right edges are the long edges.
        margin_horizontal = long_pt
        margin_vertical = short_pt
    else:
        # Landscape-like: top/bottom edges are the long edges.
        margin_horizontal = short_pt
        margin_vertical = long_pt

    return margin_horizontal, margin_vertical


def draw_crop_marks(c, x0, y0, x1, y1, mark_len, gap, line_width):
    """
    Draw small L-shaped crop marks at each of the four corners of the
    rectangle (x0, y0)-(x1, y1), offset outward by `gap`, with each leg
    `mark_len` long.
    """
    c.saveState()
    c.setLineWidth(line_width)
    c.setStrokeColorRGB(0, 0, 0)

    # Each corner: (corner_x, corner_y, x_direction, y_direction)
    # direction is -1 or +1, i.e. which way the mark points (away from box)
    corners = [
        (x0, y0, -1, -1),  # bottom-left
        (x1, y0, +1, -1),  # bottom-right
        (x0, y1, -1, +1),  # top-left
        (x1, y1, +1, +1),  # top-right
    ]

    for cx, cy, dx, dy in corners:
        # Horizontal leg
        c.line(cx + dx * gap, cy, cx + dx * (gap + mark_len), cy)
        # Vertical leg
        c.line(cx, cy + dy * gap, cx, cy + dy * (gap + mark_len))

    c.restoreState()


def build_pdf(
    image_paths,
    output_path,
    papersize_key,
    rows,
    cols,
    width_mm,
    height_mm,
    orientation="portrait",
    stretch=False,
    margin_mm=DEFAULT_MARGIN_MM,
    margin_long_mm=None,
    margin_short_mm=None,
    mark_len=DEFAULT_MARK_LENGTH_PT,
    mark_gap=DEFAULT_MARK_GAP_PT,
    mark_line_width=DEFAULT_MARK_LINE_WIDTH_PT,
):
    page_size = PAPER_SIZES[papersize_key]
    if orientation == "landscape":
        page_size = landscape(page_size)
    page_width, page_height = page_size

    margin_horizontal, margin_vertical = resolve_margins_pt(
        page_width, page_height, margin_mm, margin_long_mm, margin_short_mm
    )

    target_w_pt = width_mm * mm
    target_h_pt = height_mm * mm

    usable_width = page_width - 2 * margin_horizontal
    usable_height = page_height - 2 * margin_vertical

    if usable_width <= 0 or usable_height <= 0:
        raise LayoutError(
            "Margins leave no usable space on the page "
            f"({page_width / mm:.1f}x{page_height / mm:.1f}mm page, "
            f"{margin_horizontal / mm:.1f}mm horizontal / "
            f"{margin_vertical / mm:.1f}mm vertical margin each side)."
        )

    cell_width = usable_width / cols
    cell_height = usable_height / rows

    if target_w_pt > cell_width or target_h_pt > cell_height:
        raise LayoutError(
            f"Target image size ({width_mm}x{height_mm}mm) does not fit "
            f"into a grid cell ({cell_width / mm:.2f}x{cell_height / mm:.2f}mm) "
            f"for a {rows}x{cols} grid on {papersize_key.upper()} "
            f"{orientation} with {margin_horizontal / mm:.1f}mm horizontal / "
            f"{margin_vertical / mm:.1f}mm vertical margins. Reduce "
            f"--width-mm/--height-mm, reduce margins, reduce rows/cols, "
            f"or use a bigger paper size."
        )

    per_page = rows * cols
    total_images = len(image_paths)
    total_pages = max(1, -(-total_images // per_page))  # ceil division

    c = canvas.Canvas(output_path, pagesize=page_size)

    idx = 0
    for page_num in range(total_pages):
        for r in range(rows):
            for col in range(cols):
                if idx >= total_images:
                    break
                path = image_paths[idx]
                idx += 1

                # Cell origin (bottom-left of cell), row 0 at the top of page
                cell_x0 = margin_horizontal + col * cell_width
                cell_y0 = page_height - margin_vertical - (r + 1) * cell_height

                # Target box, centered within the cell (same for every image)
                box_x0 = cell_x0 + (cell_width - target_w_pt) / 2.0
                box_y0 = cell_y0 + (cell_height - target_h_pt) / 2.0
                box_x1 = box_x0 + target_w_pt
                box_y1 = box_y0 + target_h_pt

                draw_w, draw_h = get_draw_size_pt(
                    path, target_w_pt, target_h_pt, stretch
                )

                # Center the scaled image within the target box (matters
                # only when aspect ratio is preserved and doesn't match
                # the box's aspect ratio exactly)
                img_x0 = box_x0 + (target_w_pt - draw_w) / 2.0
                img_y0 = box_y0 + (target_h_pt - draw_h) / 2.0

                c.drawImage(
                    ImageReader(path),
                    img_x0,
                    img_y0,
                    width=draw_w,
                    height=draw_h,
                    preserveAspectRatio=False,
                    mask="auto",
                )

                # Crop marks always mark the fixed target box, so every
                # mark on the page is identical and forms a uniform grid.
                draw_crop_marks(
                    c,
                    box_x0,
                    box_y0,
                    box_x1,
                    box_y1,
                    mark_len,
                    mark_gap,
                    mark_line_width,
                )

        c.showPage()

    c.save()
    return total_pages


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Place all PNG images in a folder onto a printable PDF, each "
            "scaled to the same fixed size in millimetres, sorted by "
            "filename, arranged in a rows x cols grid per page, with "
            "corner cut marks."
        )
    )
    parser.add_argument(
        "--papersize",
        "-p",
        choices=sorted(PAPER_SIZES.keys()),
        required=True,
        help="Paper size: a3 or a4",
    )
    parser.add_argument(
        "--rows", "-r", type=int, required=True, help="Number of rows per page"
    )
    parser.add_argument(
        "--cols", "-c", type=int, required=True, help="Number of columns per page"
    )
    parser.add_argument(
        "--width-mm",
        "-w",
        type=float,
        required=True,
        help="Target width, in millimetres, that every image is scaled to",
    )
    parser.add_argument(
        "--height-mm",
        "-H",
        type=float,
        required=True,
        help="Target height, in millimetres, that every image is scaled to",
    )
    parser.add_argument(
        "--stretch",
        action="store_true",
        help=(
            "Force each image to exactly fill the width-mm x height-mm "
            "box on both axes, distorting its aspect ratio if needed. "
            "By default, aspect ratio is preserved and the image is "
            "fitted inside the box and centered."
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        default="printable_output.pdf",
        help="Output PDF filename (default: printable_output.pdf)",
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory to look for PNG files in (default: current directory)",
    )
    parser.add_argument(
        "--orientation",
        "-O",
        choices=["portrait", "landscape"],
        default="portrait",
        help="Paper orientation: portrait or landscape (default: portrait)",
    )
    parser.add_argument(
        "--margin-mm",
        type=float,
        default=DEFAULT_MARGIN_MM,
        help=(
            "Page margin in millimetres, applied to all four edges unless "
            f"overridden by --margin-long-mm / --margin-short-mm (default: {DEFAULT_MARGIN_MM})"
        ),
    )
    parser.add_argument(
        "--margin-long-mm",
        type=float,
        default=None,
        help=(
            "Margin in millimetres along the page's LONG edges (left/right "
            "on a portrait page, top/bottom on a landscape page). "
            "Overrides --margin-mm for those edges."
        ),
    )
    parser.add_argument(
        "--margin-short-mm",
        type=float,
        default=None,
        help=(
            "Margin in millimetres along the page's SHORT edges (top/bottom "
            "on a portrait page, left/right on a landscape page). "
            "Overrides --margin-mm for those edges."
        ),
    )
    parser.add_argument(
        "--mark-length",
        type=float,
        default=DEFAULT_MARK_LENGTH_PT,
        help=f"Length of each crop mark leg in points (default: {DEFAULT_MARK_LENGTH_PT})",
    )
    parser.add_argument(
        "--mark-gap",
        type=float,
        default=DEFAULT_MARK_GAP_PT,
        help=(
            "Gap between the target box edge and the start of the crop "
            f"mark, in points (default: {DEFAULT_MARK_GAP_PT})"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.rows < 1 or args.cols < 1:
        print("Error: --rows and --cols must both be at least 1.", file=sys.stderr)
        sys.exit(1)

    if args.width_mm <= 0 or args.height_mm <= 0:
        print("Error: --width-mm and --height-mm must both be positive.", file=sys.stderr)
        sys.exit(1)

    for name, value in (
        ("--margin-mm", args.margin_mm),
        ("--margin-long-mm", args.margin_long_mm),
        ("--margin-short-mm", args.margin_short_mm),
    ):
        if value is not None and value < 0:
            print(f"Error: {name} must not be negative.", file=sys.stderr)
            sys.exit(1)

    if not os.path.isdir(args.directory):
        print(f"Error: directory '{args.directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    image_paths = find_png_files(args.directory)
    if not image_paths:
        print(f"No PNG files found in '{args.directory}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(image_paths)} PNG file(s) in '{args.directory}' (sorted by filename):")
    for p in image_paths:
        print(f"  - {os.path.basename(p)}")

    try:
        total_pages = build_pdf(
            image_paths=image_paths,
            output_path=args.output,
            papersize_key=args.papersize,
            rows=args.rows,
            cols=args.cols,
            width_mm=args.width_mm,
            height_mm=args.height_mm,
            orientation=args.orientation,
            stretch=args.stretch,
            margin_mm=args.margin_mm,
            margin_long_mm=args.margin_long_mm,
            margin_short_mm=args.margin_short_mm,
            mark_len=args.mark_length,
            mark_gap=args.mark_gap,
            mark_line_width=DEFAULT_MARK_LINE_WIDTH_PT,
        )
    except LayoutError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    per_page = args.rows * args.cols
    print(
        f"\nDone. Wrote {total_pages} page(s) "
        f"({per_page} slot(s) per page, {args.papersize.upper()} "
        f"{args.orientation}, images scaled to "
        f"{args.width_mm}x{args.height_mm}mm) to '{args.output}'."
    )


if __name__ == "__main__":
    main()