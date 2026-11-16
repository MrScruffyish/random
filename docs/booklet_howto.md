# `a4_to_a3_booklet.sh`

Imposes an A4 PDF into A3 landscape sheets for booklet printing using [`pdfimpose`](https://pypi.org/project/pdfimpose/) in **hardcover** mode.

Each imposed sheet contains 2 A4 pages arranged as `2x1` on A3 landscape (`420 × 297 mm`), intended for duplex printing, folding, and binding into signatures.

## Requirements

- `bash`
- `pdfimpose` 2.9.0 (script checks for it and suggests install command)

Install:

```bash
python3 -m pip install pdfimpose==2.9.0
```

## Usage

```bash
./bin/a4_to_a3_booklet.sh INPUT.pdf [SIGNATURE_PAGES]
```

- `INPUT.pdf` — source A4 PDF (default: `guide.pdf`)
- `SIGNATURE_PAGES` — pages per signature, must be a multiple of 4 and >= 4 (default: `16`)

### Examples

```bash
# Default: 16-page signatures from guide.pdf
./bin/a4_to_a3_booklet.sh guide.pdf

# 16-page signatures (explicit)
./bin/a4_to_a3_booklet.sh guide.pdf 16

# 32-page signatures
./bin/a4_to_a3_booklet.sh guide.pdf 32
```

## Output

The script writes:

```
<basename>-A3-<SIGNATURE_PAGES>page-signatures.pdf
```

For example, `guide.pdf` with default settings becomes:

```
guide-A3-16page-signatures.pdf
```

## How it works

- Signature size in pages is converted to sheets: `SHEETS = SIGNATURE_PAGES / 4`
- Runs `pdfimpose hardcover` with:
  - `--signature 2x1`
  - `--group <SHEETS>`
  - `--bind left`
  - `--imargin 0 --omargin 0`
- No input-page scaling is requested.

## Printing recommendations

The script prints these suggested print settings on completion:

- Paper: **A3**
- Orientation: **Landscape**
- Scaling: **100% / Actual size**
- Duplex: **Yes**
- Binding: **Left**
