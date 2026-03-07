#!/usr/bin/env python3
"""
Generate a LaTeX file containing logarithm and antilogarithm tables.

Usage:
    python3 generate_log_tables.py [step [digits [paper [fontsize]]]]

Arguments:
    step      Row increment (default: 0.01).
              Columns step by step/10, mean differences by step/100.
              Examples: 0.1   -> rows 1.0,   1.1   ... 9.9
                        0.01  -> rows 1.00,  1.01  ... 9.99
                        0.001 -> rows 1.000, 1.001 ... 9.999

    digits    Number of digits in table values (default: 4).
              Use 5 for finer step sizes like 0.001.

    paper     Paper size: a3, a4 (default), a5, a6.

    fontsize  Base font size in pt (default: 10).

Examples:
    python3 generate_log_tables.py
    python3 generate_log_tables.py 0.01 4 a4 10
    python3 generate_log_tables.py 0.001 5 a3 11
    python3 generate_log_tables.py 0.1 4 a5 9
"""

import math
import sys

VALID_PAPERS = {"a3", "a4", "a5", "a6"}


def decimal_places(f):
    s = f"{f:.10f}".rstrip('0')
    return len(s.split('.')[1]) if '.' in s else 0


def build_header(col_spec):
    """Single-row header: x | 0 1 2 3 4 5 6 7 8 9 | 1 2 3 4 5 6 7 8 9"""
    header_main = " & ".join(f"\\textbf{{{i}}}" for i in range(10))
    header_diff = " & ".join(f"\\textbf{{{i}}}" for i in range(1, 10))
    row = (r"\multicolumn{1}{c|}{\textbf{x}} & "
           + header_main + " & " + header_diff + r" \\")
    return "\n".join([
        f"\\begin{{longtable}}{{{col_spec}}}",
        r"\hline",
        row,
        r"\hline",
        r"\endfirsthead",
        r"\hline",
        row,
        r"\hline",
        r"\endhead",
        r"\hline",
        r"\endlastfoot",
    ])


def log_row(x, col_step, digits):
    scale = 10 ** digits
    dp    = decimal_places(col_step * 10)
    label = f"{x:.{dp}f}"
    main  = " & ".join(
                f"{round((math.log10(x + j*col_step) % 1) * scale):0{digits}d}"
                for j in range(10))
    base  = math.log10(x) % 1
    diffs = " & ".join(
                str(abs(round(((math.log10(x + d*(col_step/10)) % 1) - base) * scale)))
                for d in range(1, 10))
    return f"{label} & {main} & {diffs} \\\\"


def antilog_row(x, col_step, digits):
    scale = 10 ** (digits - 1)
    dp    = decimal_places(col_step * 10)
    label = f"{x:.{dp}f}"
    main  = " & ".join(
                f"{round(10**(x + j*col_step) * scale):0{digits}d}"
                for j in range(10))
    base  = 10**x
    diffs = " & ".join(
                str(abs(round((10**(x + d*(col_step/10)) - base) * scale)))
                for d in range(1, 10))
    return f"{label} & {main} & {diffs} \\\\"


def build_table(title, row_start, row_end, col_step, digits, row_fn, is_antilog):
    col_spec   = "c|" + "c"*10 + "|" + "c"*9
    rows = []
    x = row_start
    while x < row_end - 1e-9:
        rows.append(row_fn(x, col_step, digits))
        x = round(x + col_step * 10, 10)
    return "\n".join([
        f"\\section*{{{title}}}",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        build_header(col_spec),
        *rows,
        r"\hline",
        r"\end{longtable}",
    ])


def generate_latex(step, digits, paper, fontsize):
    col_step = step / 10
    doc_opts = f"{paper}paper,{fontsize}pt"
    preamble = f"""\\documentclass[{doc_opts}]{{article}}
\\usepackage[{paper}paper, margin=1.5cm]{{geometry}}
\\usepackage{{longtable}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
\\usepackage{{microtype}}

\\title{{\\textbf{{Mathematical Tables}}\\\\[0.5em]\\large Logarithms and Antilogarithms}}
\\date{{}}

\\begin{{document}}
\\maketitle
\\thispagestyle{{empty}}

\\noindent\\textbf{{How to use the log table:}} Find the row for the leading significant
figures of your number, then the column for the next digit. For greater precision, look up
the final digit in the right-hand part of the table (mean differences) and add that value.
The result is the mantissa; add the characteristic separately.

\\bigskip
\\noindent\\textbf{{How to use the antilog table:}} Use the decimal part (mantissa) of
the logarithm. Find the row for the first digits, column for the next. For greater precision,
look up the final digit in the right-hand part of the table (mean differences) and add that
value. Apply the characteristic to place the decimal point.
\\
\\vspace{{1em}}
"""
    log_t     = build_table(f"{digits}-Figure Logarithm Table",
                            1.0, 10.0, col_step, digits, log_row, False)
    antilog_t = build_table(f"{digits}-Figure Antilogarithm Table",
                            0.0,  1.0, col_step, digits, antilog_row, True)
    return preamble + log_t + "\n\\newpage\n" + antilog_t + "\n\\end{document}\n"


def parse_args():
    step     = 0.01
    digits   = 4
    paper    = "a4"
    fontsize = 10

    if len(sys.argv) > 1:
        try:
            step = float(sys.argv[1])
            if not (0 < step < 1):
                raise ValueError
        except ValueError:
            print("Error: step must be a float between 0 and 1 (e.g. 0.1, 0.01, 0.001)")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            digits = int(sys.argv[2])
            if digits < 1:
                raise ValueError
        except ValueError:
            print("Error: digits must be a positive integer (e.g. 4 or 5)")
            sys.exit(1)

    if len(sys.argv) > 3:
        paper = sys.argv[3].lower()
        if paper not in VALID_PAPERS:
            print(f"Error: paper must be one of: {', '.join(sorted(VALID_PAPERS))}")
            sys.exit(1)

    if len(sys.argv) > 4:
        try:
            fontsize = int(sys.argv[4])
            if fontsize < 1:
                raise ValueError
        except ValueError:
            print("Error: fontsize must be a positive integer (e.g. 10, 11, 12)")
            sys.exit(1)

    return step, digits, paper, fontsize


if __name__ == "__main__":
    step, digits, paper, fontsize = parse_args()
    content = generate_latex(step, digits, paper, fontsize)
    output_path = "log_antilog_tables.tex"
    with open(output_path, "w") as f:
        f.write(content)
    col_step = step / 10
    print(f"Written: {output_path}")
    print(f"  row_step={step}, col_step={col_step}, diff_step={col_step/10}")
    print(f"  digits={digits}, paper={paper.upper()}, fontsize={fontsize}pt")
    print("To compile: pdflatex log_antilog_tables.tex")