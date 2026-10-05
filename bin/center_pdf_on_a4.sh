#!/usr/bin/env python3
"""
Center every page of a PDF onto A4 paper, with no scaling -- just padding.

Usage:
    python3 center_on_a4.py input.pdf output.pdf
"""

import sys
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject

A4_WIDTH_PT = 595.2756   # 210 mm
A4_HEIGHT_PT = 841.8898  # 297 mm


def center_on_a4(input_path: str, output_path: str):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        src_w = float(page.mediabox.width)
        src_h = float(page.mediabox.height)

        if src_w > A4_WIDTH_PT or src_h > A4_HEIGHT_PT:
            print(
                f"  [warn] page {i+1} ({src_w:.1f}x{src_h:.1f}pt) is larger than "
                f"A4 ({A4_WIDTH_PT:.1f}x{A4_HEIGHT_PT:.1f}pt) in at least one "
                f"dimension -- it will hang off the edge since this script "
                f"never scales content down.",
                file=sys.stderr,
            )

        # Offset to center the original page on an A4 canvas.
        dx = (A4_WIDTH_PT - src_w) / 2
        dy = (A4_HEIGHT_PT - src_h) / 2

        # Build a blank A4 page, then stamp the original page's content onto
        # it, shifted by (dx, dy). add_transformation moves the page's
        # existing content; merge_page draws another page on top of this one.
        blank = writer.add_blank_page(width=A4_WIDTH_PT, height=A4_HEIGHT_PT)
        page.add_transformation(Transformation().translate(tx=dx, ty=dy))
        # After translating, the page's own mediabox/cropbox still reports the
        # old (smaller) box, so widen it back out before merging or content
        # outside the original box could get clipped.
        page.mediabox = RectangleObject((0, 0, A4_WIDTH_PT, A4_HEIGHT_PT))
        if page.cropbox is not None:
            page.cropbox = RectangleObject((0, 0, A4_WIDTH_PT, A4_HEIGHT_PT))
        blank.merge_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 center_on_a4.py input.pdf output.pdf", file=sys.stderr)
        sys.exit(1)
    center_on_a4(sys.argv[1], sys.argv[2])
    print(f"Wrote {sys.argv[2]}")