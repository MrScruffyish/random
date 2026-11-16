#!/usr/bin/env python3

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# sudo apt install python3-pil

HELP = """\
Usage:
    compose.py CONFIG_FILE OUTPUT_FILE

Create an image by placing PNG images and text using Cartesian coordinates.

Configuration format:

    WIDTH HEIGHT
    X Y IMAGE_FILENAME
    text FONT_SIZE X Y TEXT

Example:

    640 480
    30 40 img1.png
    40 120 img2.png
    200 300 img3.png
    text 32 100 200 Hello, this is some text
    text 24 100 150 Another piece of text

Coordinates use the standard mathematical Cartesian system:
    (0, 0) is the bottom-left corner.
    X increases to the right.
    Y increases upwards.

For images, X Y specifies the bottom-left corner of the image.

For text, X Y specifies the bottom-left corner of the text.

Text can contain spaces and does not need quotes.

The text is rendered using a bold, easy-to-read font.

Example:

    compose.py layout.txt output.png
"""


def find_bold_font():
    """Find a suitable bold font available on common Linux systems."""

    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]

    for font in fonts:
        if Path(font).is_file():
            return font

    raise RuntimeError(
        "Could not find a suitable bold font. "
        "Install the DejaVu fonts, for example:\n"
        "    sudo apt install fonts-dejavu"
    )


def read_config(filename):
    """Read image size and placement instructions."""

    instructions = []

    with open(filename, "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]

    if not lines:
        raise ValueError("Configuration file is empty")

    # First line: width height
    first = lines[0].split()

    if len(first) != 2:
        raise ValueError(
            "First line must contain width and height, for example: 640 480"
        )

    width, height = map(int, first)

    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive")

    # Remaining lines
    for line_number, line in enumerate(lines[1:], start=2):

        parts = line.split(maxsplit=3)

        # Text instruction:
        #
        # text FONT_SIZE X Y TEXT
        #
        # split(maxsplit=3) leaves everything after Y together.
        if parts[0].lower() == "text":

            if len(parts) != 4:
                raise ValueError(
                    f"Invalid text instruction at line {line_number}:\n"
                    f"    {line}\n"
                    f"Expected: text FONT_SIZE X Y TEXT"
                )

            font_size = int(parts[1])
            x = int(parts[2])
            y = int(parts[3].split(maxsplit=1)[0])

            text_parts = parts[3].split(maxsplit=1)

            if len(text_parts) != 2:
                raise ValueError(
                    f"Missing text at line {line_number}"
                )

            text = text_parts[1]

            if font_size <= 0:
                raise ValueError(
                    f"Font size must be positive at line {line_number}"
                )

            instructions.append(
                ("text", font_size, x, y, text)
            )

        else:
            # Image instruction:
            #
            # X Y FILENAME
            #
            parts = line.split(maxsplit=2)

            if len(parts) != 3:
                raise ValueError(
                    f"Invalid image instruction at line {line_number}:\n"
                    f"    {line}\n"
                    f"Expected: X Y FILENAME"
                )

            x = int(parts[0])
            y = int(parts[1])
            filename = parts[2]

            instructions.append(
                ("image", x, y, filename)
            )

    return width, height, instructions


def create_image(config_file, output_file):
    width, height, instructions = read_config(config_file)

    # Transparent RGBA canvas.
    canvas = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(canvas)

    font_path = find_bold_font()

    for instruction in instructions:

        if instruction[0] == "image":

            _, x, y, filename = instruction

            print(f"Placing image {filename} at ({x}, {y})")

            image = Image.open(filename).convert("RGBA")

            # Convert Cartesian bottom-left coordinates to
            # Pillow's top-left coordinate system.
            pillow_y = height - y - image.height

            canvas.alpha_composite(
                image,
                (x, pillow_y)
            )

            # Recreate the drawing object after compositing.
            draw = ImageDraw.Draw(canvas)

        elif instruction[0] == "text":

            _, font_size, x, y, text = instruction

            print(
                f'Writing text "{text}" '
                f"at ({x}, {y}), size {font_size}"
            )

            font = ImageFont.truetype(
                font_path,
                font_size
            )

            # Pillow's text anchor "ls" means:
            #   l = left
            #   s = baseline
            #
            # We want the supplied Cartesian Y coordinate
            # to represent the bottom/baseline of the text.
            pillow_y = height - y

            draw.text(
                (x, pillow_y),
                text,
                font=font,
                fill=(0, 0, 0, 255),
                anchor="ls"
            )

    canvas.save(output_file)

    print(
        f"Created {output_file} "
        f"({width}x{height})"
    )


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h"):
        print(HELP)
        return

    if len(sys.argv) != 3:
        print(HELP, file=sys.stderr)
        sys.exit(1)

    config_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        create_image(config_file, output_file)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()