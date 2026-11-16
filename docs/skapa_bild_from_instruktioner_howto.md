# `skapa_bild_from_instruktioner.py`

Composes a PNG image from a text instruction file by placing PNG images and rendering text onto a transparent canvas.

Coordinates use a **Cartesian** system:
- `(0, 0)` is the **bottom-left** corner
- X increases to the right
- Y increases upward

(The script converts to Pillow's top-left coordinate system internally.)

## Requirements

- Python 3
- [Pillow](https://python-pillow.org/)

On Debian/Ubuntu:

```bash
sudo apt install python3-pil
```

A bold font is required for text rendering. The script looks for common fonts such as DejaVu Sans Bold and Liberation Sans Bold. If none is found, install:

```bash
sudo apt install fonts-dejavu
```

## Usage

```bash
./bin/skapa_bild_from_instruktioner.py CONFIG_FILE OUTPUT_FILE
```

- `CONFIG_FILE` — text file describing canvas size and drawing instructions
- `OUTPUT_FILE` — output image path (e.g. `output.png`)

Show help:

```bash
./bin/skapa_bild_from_instruktioner.py --help
```

## Configuration format

- Blank lines and lines starting with `#` are ignored.
- **First line:** canvas size

```text
WIDTH HEIGHT
```

- **Image placement:**

```text
X Y IMAGE_FILENAME
```

`X Y` is the **bottom-left corner** of the placed image.

- **Text placement:**

```text
text FONT_SIZE X Y TEXT...
```

`X Y` is the **bottom-left/baseline position** for the text in Cartesian coordinates. `TEXT` may contain spaces.

## Example config

```text
640 480
30 40 img1.png
40 120 img2.png
200 300 img3.png
text 32 100 200 Hello, this is some text
text 24 100 150 Another piece of text
```

## Output details

- Canvas: RGBA, fully transparent background `(0, 0, 0, 0)`
- Placed images are composited with alpha (`alpha_composite`)
- Text is rendered in **black** (`255` alpha) using a bold font
- Progress/errors are printed to stdout/stderr
