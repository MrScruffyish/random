# random

Small collection of personal scripts and utilities.

## Binaries (`bin/`)

| Script | Description | Documentation |
|---|---|---|
| `a4_to_a3_booklet.sh` | Imposes an A4 PDF into A3 landscape booklet signatures for duplex printing/folding using `pdfimpose` (default: 16-page signatures). | [docs/booklet_howto.md](docs/booklet_howto.md) |
| `center_pdf_on_a4.sh` | Centers each page of a PDF onto an A4 canvas without scaling (pads with margins) using `pypdf`. | [docs/center_pdf_on_a4_howto.md](docs/center_pdf_on_a4_howto.md) |
| `center_pdf_on_a4_compress.sh` | Same as `center_pdf_on_a4.sh`, but also compresses content streams and attempts to deduplicate identical PDF objects to reduce output size. | [docs/center_pdf_on_a4_howto.md](docs/center_pdf_on_a4_howto.md) |
| `skapa_bild_from_instruktioner.py` | Composes a PNG image by placing PNG images and text on a transparent canvas from a simple coordinate-based instruction file (Cartesian coordinates). | [docs/skapa_bild_from_instruktioner_howto.md](docs/skapa_bild_from_instruktioner_howto.md) |
| `skapa_kalender.py` | Generates weekly calendars as PDF and PostScript for A3/A4, portrait/landscape, with optional dated/recurring text entries. | [docs/kalender_howto.md](docs/kalender_howto.md) |
| `skapa_pdf_from_many_images.py` | Arranges PNG images from a directory into a printable grid PDF (A3/A4), scaling each image to a fixed size and drawing cut/crop marks. | [docs/skapa_pdf_from_many_images_howto.md](docs/skapa_pdf_from_many_images_howto.md) |
| `text2png.sh` | Renders a plain text file to a PNG image using ImageMagick/Pango (monospaced, white background). | [docs/text2png_howto.md](docs/text2png_howto.md) |

## Docs

Additional usage details live in [`docs/`](docs/).

