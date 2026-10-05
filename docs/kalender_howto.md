# Calendar Entry File Format

Entry files let you overlay text notes (shown as bullet points) inside each
day box of the generated calendar. Pass one or more files with `--entries`:

```
python3 make_calendar.py --paper a3 --entries holidays.txt 2026
python3 make_calendar.py --paper a4 --entries work.txt --entries personal.txt 2026
```

---

## File format

One entry per line. Blank lines and lines starting with `#` are ignored.

### 1. Plain date

```
YYYY-MM-DD  Some text
```

Adds the text to that single day.

**Example:**
```
2026-12-25  Juldagen
2026-01-01  Nyårsdagen
```

---

### 2. Single offset: `+N`

```
YYYY-MM-DD+N  Some text
```

Adds the text twice. On the base date and once, **N days after** the base date. `+1` means the following
day, `+7` means one week later.

**Example:**
```
# Mark the day and the following day
2026-03-09+1  Something 2 days
```

---

### 3. Repeating: `+N*M`

```
YYYY-MM-DD+N*M  Some text
```

Adds the text **M times total**, starting on the base date and repeating
every N days:

- First entry: `YYYY-MM-DD` (the base date itself)
- Second entry: `YYYY-MM-DD + N`
- ...
- Last (Mth) entry: `YYYY-MM-DD + N × (M−1)`

So `+7*4` means 4 entries on weeks 0, 1, 2, 3 relative to the base date.

**Example:**
```
# Weekly team meeting every Monday, 4 weeks (including the first Monday)
2026-01-05+7*4  Veckostämma

# Medication every 5 days, 3 doses (starting today)
2026-02-01+5*3  Ta medicin
```

**Comparison of forms:**

| Syntax           | Entries on                | Count |
|------------------|---------------------------|-------|
| `2026-01-05`     | 2026-01-05                | 1     |
| `2026-01-05+7`   | 2026-01-12                | 1     |
| `2026-01-05+7*4` | 2026-01-05, -12, -19, -26 | 4     |

---

## Text display

- Entries appear as bullet points (`•`) below the date label in each day box.
- Text is shown in dark blue for dates inside the calendar range, muted blue
  for dates in partial weeks outside the range.
- If the text is too wide for the box, the font is scaled down slightly
  (up to 15% smaller than the base size).
- If it is still too wide after scaling, the text is truncated with `…`.
- If there are more entries than fit vertically in the box, the excess are
  silently omitted — use `--rows` with a smaller value to get taller boxes.

---

## Full example file

```
# Public holidays Sweden 2026
2026-01-01  Nyårsdagen
2026-01-06  Trettondedag jul
2026-04-03  Långfredag
2026-04-06  Annandag påsk
2026-05-01  Första maj
2026-05-21  Kristi himmelsfärdsdag
2026-06-06  Nationaldagen
2026-06-20  Midsommarafton
2026-12-24  Julafton
2026-12-25  Juldagen
2026-12-26  Annandag jul
2026-12-31  Nyårsafton

# Weekly standup every Monday for 8 weeks starting 2026-01-05 (8 entries)
2026-01-05+7*8  Standup 09:00

# Quarterly review (manually listed)
2026-03-31  Q1 review
2026-06-30  Q2 review
2026-09-30  Q3 review
2026-12-31  Q4 review
```