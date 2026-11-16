# `center_pdf_on_a4.sh` and `center_pdf_on_a4_compress.sh`

Python scripts (with `.sh` filenames) that place every page of a PDF onto an A4 canvas **without scaling**. The original page content is centered and padded to A4 size.

- `center_pdf_on_a4.sh` — basic centering.
- `center_pdf_on_a4_compress.sh` — same centering, plus output-size reduction steps.

## Requirements

- Python 3
- [`pypdf`](https://pypi.org/project/pypdf/)

Install:

```bash
python3 -m pip install pypdf
```

For best compression/deduplication results with `center_pdf_on_a4_compress.sh`, use a recent `pypdf`:

```bash
python3 -m pip install --upgrade pypdf
```

## Usage

```bash
./bin/center_pdf_on_a4.sh input.pdf output.pdf
./bin/center_pdf_on_a4_compress.sh input.pdf output.pdf
```

(You can also run them explicitly with `python3`, e.g. `python3 bin/center_pdf_on_a4.sh in.pdf out.pdf`.)

## Behavior

- Target page size: **A4** (`210 × 297 mm`, `595.2756 × 841.8898 pt`).
- Each source page is translated so it is centered on an A4 page.
- **No scaling** is applied.
  - If a source page is larger than A4 in any dimension, a warning is printed to stderr; content may extend beyond the page edges.
- Media/crop boxes are expanded to A4 to avoid clipping after translation.

## Compression variant extras (`center_pdf_on_a4_compress.sh`)

After composing pages, this script:

1. Calls `compress_content_streams()` on each page when available.
2. Calls `writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)` when available (newer `pypdf`).
3. Prints a note to stderr if `compress_identical_objects()` is unavailable and suggests upgrading `pypdf`.

This can significantly reduce size for image-heavy PDFs where page merging would otherwise duplicate shared objects on older `pypdf` versions.
