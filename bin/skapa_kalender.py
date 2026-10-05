#!/usr/bin/env python3
"""
Generate A3/A4 portrait or landscape weekly calendar as PDF and PS.

Usage:
  python3 make_calendar.py --paper a3 2026-01 2026-03
  python3 make_calendar.py --paper a4 2026
  python3 make_calendar.py --paper a3 --landscape 2026-01 2026-06
  python3 make_calendar.py --paper a4 --landscape --rows 6 2026
  python3 make_calendar.py --paper a3 --entries holidays.txt 2026
  python3 make_calendar.py --paper a3 --entries a.txt --entries b.txt 2026
  python3 make_calendar.py --paper a3 2026-01 2026-03 myfile
"""

import sys, re, argparse, calendar
from datetime import date, timedelta
from collections import defaultdict
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A3, A4, landscape as rl_landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_REG  = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
pdfmetrics.registerFont(TTFont(FONT_REG,  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont(FONT_BOLD, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

DAYS_SV = ["Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"]
BULLET  = "\u2022"

# ── Entry file parsing ─────────────────────────────────────────────────────
def parse_entries(filenames):
    """
    Returns dict: date -> [text, ...]
    Line formats:
      YYYY-MM-DD text
      YYYY-MM-DD+N text          add entry N days after base (once)
      YYYY-MM-DD+N*M text        add entry at base+N, base+2N, ... base+M*N
    Lines starting with # are comments.
    """
    entries = defaultdict(list)
    pat = re.compile(
        r'^(\d{4}-\d{2}-\d{2})'
        r'(?:\+(\d+))?'
        r'(?:\*(\d+))?'
        r'\s+(.*?)\s*$'
    )
    for filename in filenames:
        with open(filename, encoding='utf-8') as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                m = pat.match(line)
                if not m:
                    print(f"  Warning: {filename}:{lineno}: unrecognised line skipped: {line!r}",
                          file=sys.stderr)
                    continue
                base_str, interval_str, count_str, text = m.groups()
                try:
                    base = date.fromisoformat(base_str)
                except ValueError:
                    print(f"  Warning: {filename}:{lineno}: bad date {base_str!r}, skipped",
                          file=sys.stderr)
                    continue
                interval = int(interval_str) if interval_str else None
                count    = int(count_str)    if count_str    else None
                if interval is None:
                    entries[base].append(text)
                elif count is None:
                    # +N only: on base and one entry N days after base
                    entries[base].append(text)
                    entries[base + timedelta(days=interval)].append(text)
                else:
                    # +N*M: M entries at base, base+N, ..., base+(M-1)*N
                    for i in range(count):
                        entries[base + timedelta(days=interval * i)].append(text)
    return entries

# ── Date range helpers ─────────────────────────────────────────────────────
def parse_ym(s):
    parts = s.strip().split("-")
    return (int(parts[0]), None) if len(parts) == 1 else (int(parts[0]), int(parts[1]))

def expand_range(start_arg, end_arg):
    sy, sm = parse_ym(start_arg)
    full   = sm is None
    if sm is None: sm = 1
    if end_arg is None:
        return (sy, sm), (sy, 12 if full else sm)
    ey, em = parse_ym(end_arg)
    if em is None: em = 12
    return (sy, sm), (ey, em)

def get_weeks(start_ym, end_ym):
    start = date(start_ym[0], start_ym[1], 1)
    end   = date(end_ym[0], end_ym[1], calendar.monthrange(*end_ym)[1])
    cur   = start - timedelta(days=start.weekday())
    weeks = []
    while cur <= end:
        weeks.append([cur + timedelta(days=i) for i in range(7)])
        cur += timedelta(days=7)
    return weeks

def paginate(weeks, rows):
    return [weeks[i:i+rows] for i in range(0, len(weeks), rows)]

def lay(pw, ph, n):
    ml=mr=10*mm; mt=12*mm; mb=10*mm
    wc=20*mm; hh=9*mm
    tw=pw-ml-mr; dw=(tw-wc)/7; th=ph-mt-mb-hh; rh=th/n
    return ml,mr,mt,mb,wc,hh,tw,dw,th,rh

# ── PDF ────────────────────────────────────────────────────────────────────
def generate_pdf(pages, start_ym, end_ym, outfile, pw, ph, entries):
    today = date.today()
    c = rl_canvas.Canvas(outfile, pagesize=(pw, ph))
    c.setTitle(f"Kalender {start_ym[0]}-{start_ym[1]:02d} \u2013 {end_ym[0]}-{end_ym[1]:02d}")
    for pw_ in pages:
        _pdf_page(c, pw_, start_ym, end_ym, today, pw, ph, entries)
        c.showPage()
    c.save()
    print(f"  PDF: {outfile}")

def _pdf_page(c, weeks, start_ym, end_ym, today, pw, ph, entries):
    n = len(weeks)
    ml,mr,mt,mb,wc,hh,tw,dw,rh_,rh = lay(pw,ph,n)

    def colx(col): return ml + (0 if col==0 else wc + dw*(col-1))
    def ytop(row): return ph - mt - hh - row*rh

    # backgrounds
    c.setFillColor(colors.HexColor("#DDDBD4"))
    c.rect(ml, ph-mt-hh, tw, hh, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#EFEFEB"))
    for d in [5,6]:
        c.rect(colx(d+1), ph-mt-hh-n*rh, dw, n*rh, fill=1, stroke=0)
    #Dont mark current week.
    #for r,week in enumerate(weeks):
    #    if any(d==today for d in week):
    #        c.setFillColor(colors.HexColor("#FAFAE0"))
    #        c.rect(ml, ytop(r)-rh, tw, rh, fill=1, stroke=0)

    # grid
    c.setStrokeColor(colors.HexColor("#999999")); c.setLineWidth(0.4)
    for r in range(n+1):
        y=ytop(r); c.line(ml,y,ml+tw,y)
    c.line(ml, ph-mt, ml+tw, ph-mt)
    for col in range(9):
        x = colx(col) if col<8 else ml+tw
        if col==8: x=ml+tw
        c.line(x, ph-mt, x, ph-mt-hh-n*rh)

    # header text
    fsz = min(7.5, dw/mm*0.45)
    c.setFillColor(colors.black)
    hcy = ph-mt-hh+hh*0.3

    def ctr(txt, cx, cy, fs=None, bold=True):
        f = FONT_BOLD if bold else FONT_REG
        sz = fs or fsz
        c.setFont(f,sz); w=c.stringWidth(txt,f,sz); c.drawString(cx-w/2,cy,txt)

    ctr("Vecka", ml+wc/2, hcy)
    for d,name in enumerate(DAYS_SV):
        ctr(name, colx(d+1)+dw/2, hcy)

    date_fs = max(4.5, min(6.5, rh/mm*0.28))
    wk_fs   = max(5,   min(8,   rh/mm*0.35))
    efs     = max(5.5, min(7.5, rh/mm*0.34))   # larger than date_fs
    pad     = 1.5*mm

    for r,week in enumerate(weeks):
        yt = ytop(r)
        ctr(str(week[0].isocalendar()[1]), ml+wc/2, yt-rh*0.52, fs=wk_fs)
        for d,day in enumerate(week):
            in_r = start_ym <= (day.year,day.month) <= end_ym
            c.setFillColor(colors.HexColor("#AAAAAA") if not in_r else colors.black)
            c.setFont(FONT_REG, date_fs)
            dx = colx(d+1)+pad
            c.drawString(dx, yt-4*mm, day.strftime("%Y-%m-%d"))

            for i,text in enumerate(entries.get(day,[])):
                ey = yt - 4*mm - date_fs*1.1 - 1.5*mm - i*efs*1.25
                if ey < yt-rh+1*mm: break
                bt = f"{BULLET} {text}"
                fs = efs
                c.setFont(FONT_REG, fs)
                aw = dw - 2*pad
                tw_ = c.stringWidth(bt, FONT_REG, fs)
                if tw_ > aw:
                    fs2 = max(fs*0.85, fs*aw/tw_)
                    fs = fs2; c.setFont(FONT_REG, fs)
                    tw_ = c.stringWidth(bt, FONT_REG, fs)
                if tw_ > aw:
                    while bt and c.stringWidth(bt+"\u2026",FONT_REG,fs)>aw:
                        bt=bt[:-1]
                    bt+="\u2026"
                c.setFillColor(colors.HexColor("#555555") if not in_r else colors.black)
                c.drawString(dx, ey, bt)

# ── PS ─────────────────────────────────────────────────────────────────────
def generate_ps(pages, start_ym, end_ym, outfile, pw, ph, entries):
    today = date.today()

    def ps_str(text):
        out=[]
        for ch in text:
            try: b=ch.encode('latin-1')[0]
            except: b=ord('?')
            if b in (40,41,92): out.append(f'\\{chr(b)}')
            elif b>127: out.append(f'\\{b:03o}')
            else: out.append(ch)
        return '('+''.join(out)+')'

    def pt(v): return f"{v:.2f}"

    lines = [
        "%!PS-Adobe-3.0",
        f"%%BoundingBox: 0 0 {round(pw)} {round(ph)}",
        f"%%Pages: {len(pages)}",
        "%%DocumentFonts: Helvetica Helvetica-Bold",
        "%%EndComments","%%BeginProlog",
        "% reencodeISO: /NewName /OldName reencodeISO",
        "/reencodeISO {",
        "  findfont dup length dict begin",
        "  { 1 index /FID ne { def } { pop pop } ifelse } forall",
        "  /Encoding ISOLatin1Encoding def currentdict end definefont pop",
        "} def",
        "/HelveticaISO     /Helvetica      reencodeISO",
        "/HelveticaBoldISO /Helvetica-Bold reencodeISO",
        "/SF  { /HelveticaISO     findfont exch scalefont setfont } def",
        "/SFB { /HelveticaBoldISO findfont exch scalefont setfont } def",
        "% showctr: cx cy (str) showctr  -- centers string horizontally at cx,cy",
        "/showctr {",
        "  /sc_s exch def /sc_y exch def /sc_x exch def",
        "  sc_x sc_s stringwidth pop 2 div sub sc_y moveto sc_s show",
        "} def",
        "% drawbullet: x y fontsize drawbullet -- filled circle bullet",
        "/drawbullet {",
        "  /dbs exch def /dby exch def /dbx exch def",
        "  dbx dbs 0.35 mul add  dby dbs 0.28 mul add  dbs 0.18 mul  0 360 arc fill",
        "} def",
        "%%EndProlog",
    ]

    for pi,weeks in enumerate(pages):
        n=len(weeks)
        ml,mr,mt,mb,wc,hh,tw,dw,rh_,rh = lay(pw,ph,n)
        def colx(col): return ml+(0 if col==0 else wc+dw*(col-1))
        def ytop(row): return ph-mt-hh-row*rh

        lines.append(f"%%Page: {pi+1} {pi+1}")
        lines += ["1 setgray",f"0 0 {pt(pw)} {pt(ph)} rectfill","0 setgray"]

        lines += ["0.867 0.859 0.831 setrgbcolor",
                  f"{pt(ml)} {pt(ph-mt-hh)} {pt(tw)} {pt(hh)} rectfill","0 setgray"]
        lines.append("0.937 0.937 0.922 setrgbcolor")
        for d in [5,6]:
            x=colx(d+1)
            lines.append(f"{pt(x)} {pt(ph-mt-hh-n*rh)} {pt(dw)} {pt(n*rh)} rectfill")
        for r,week in enumerate(weeks):
            if any(d==today for d in week):
                yt=ytop(r)
                lines += ["0.980 0.980 0.875 setrgbcolor",
                          f"{pt(ml)} {pt(yt-rh)} {pt(tw)} {pt(rh)} rectfill"]
        lines.append("0 setgray")

        lines.append("0.6 setgray 0.4 setlinewidth")
        for r in range(n+1):
            y=ytop(r); lines.append(f"{pt(ml)} {pt(y)} moveto {pt(ml+tw)} {pt(y)} lineto stroke")
        lines.append(f"{pt(ml)} {pt(ph-mt)} moveto {pt(ml+tw)} {pt(ph-mt)} lineto stroke")
        for col in range(9):
            x=colx(col) if col<8 else ml+tw
            if col==8: x=ml+tw
            lines.append(f"{pt(x)} {pt(ph-mt)} moveto {pt(x)} {pt(ph-mt-hh-n*rh)} lineto stroke")
        lines.append("0 setgray")

        fsz=min(7.5, dw/mm*0.45); hcy=ph-mt-hh+hh*0.3
        lines.append(f"{fsz:.1f} SFB")
        lines.append(f"{pt(ml+wc/2)} {pt(hcy)} (Vecka) showctr")
        for d,name in enumerate(DAYS_SV):
            cx=colx(d+1)+dw/2
            lines.append(f"{pt(cx)} {pt(hcy)} {ps_str(name)} showctr")

        date_fs=max(4.5,min(6.5,rh/mm*0.28))
        wk_fs  =max(5,  min(8,  rh/mm*0.35))
        efs    =max(5.5,min(7.5,rh/mm*0.34))   # larger than date_fs
        pad    =1.5*mm

        for r,week in enumerate(weeks):
            yt=ytop(r)
            lines.append(f"{wk_fs:.1f} SFB")
            lines.append(f"{pt(ml+wc/2)} {pt(yt-rh*0.52)} ({week[0].isocalendar()[1]}) showctr")
            lines.append(f"{date_fs:.1f} SF")
            for d,day in enumerate(week):
                in_r = start_ym<=(day.year,day.month)<=end_ym
                lines.append(f"{'0' if in_r else '0.67'} setgray")
                dx=colx(d+1)+pad; dy=yt-4*mm
                lines.append(f"{pt(dx)} {pt(dy)} moveto {ps_str(day.strftime('%Y-%m-%d'))} show")

                day_ents = entries.get(day,[])
                if day_ents:
                    ec = "0 setgray" if in_r else "0.4 setgray"
                    aw = dw - 2*pad
                    for i,text in enumerate(day_ents):
                        ey = dy - date_fs*1.1 - 1.5*mm - i*efs*1.25
                        if ey < yt-rh+1*mm: break
                        # bullet indent = ~1.2 * fontsize
                        indent = efs * 0.72
                        bt = text   # bullet drawn separately
                        fs = efs
                        tw_e = len(bt)*fs*0.55
                        text_aw = aw - indent
                        if tw_e > text_aw:
                            fs2 = max(fs*0.85, fs*text_aw/tw_e)
                            fs=fs2; tw_e=len(bt)*fs*0.55
                        if tw_e > text_aw:
                            mc = max(3, int(text_aw/(fs*0.55))-1)
                            bt = bt[:mc]+"~"
                        lines.append(f"{fs:.2f} SF")
                        lines.append(ec)
                        # draw bullet circle then text
                        lines.append(f"{pt(dx)} {pt(ey)} {fs:.2f} drawbullet")
                        lines.append(f"{pt(dx + indent)} {pt(ey)} moveto {ps_str(bt)} show")

        lines.append("showpage")

    lines.append("%%EOF")
    with open(outfile,'w',encoding='latin-1') as f:
        f.write('\n'.join(lines)+'\n')
    print(f"  PS:  {outfile}")

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Generate A3/A4 weekly calendar as PDF and PS.")
    p.add_argument("--paper",     required=True, choices=["a3","a4"])
    p.add_argument("--landscape", action="store_true")
    p.add_argument("--rows",      type=int, default=None,
                   help="Weeks per page (defaults: A3 portrait=14, landscape=8; A4 portrait=10, landscape=6)")
    p.add_argument("--entries",   metavar="FILE", action="append", default=[],
                   help="Entry file to overlay on days (repeatable)")
    p.add_argument("start",  help="YYYY-MM or YYYY")
    p.add_argument("end",    nargs="?", default=None, help="YYYY-MM or YYYY (optional)")
    p.add_argument("basename",nargs="?",default=None, help="Output basename")
    args = p.parse_args()

    start_ym, end_ym = expand_range(args.start, args.end)
    base_size = A3 if args.paper=="a3" else A4
    pw,ph = rl_landscape(base_size) if args.landscape else base_size

    rows = args.rows or (8 if args.landscape else 14 if args.paper=="a3" else 6 if args.landscape else 10)
    if not args.rows:
        rows = (8 if args.landscape else 14) if args.paper=="a3" else (6 if args.landscape else 10)

    entries = parse_entries(args.entries) if args.entries else {}
    if entries:
        print(f"  Entries: {sum(len(v) for v in entries.values())} items across {len(entries)} dates")

    weeks  = get_weeks(start_ym, end_ym)
    pages_ = paginate(weeks, rows)
    ls     = f"{start_ym[0]}-{start_ym[1]:02d}"; le=f"{end_ym[0]}-{end_ym[1]:02d}"
    base   = args.basename or f"calendar_{ls}_{le}"
    orient = "landscape" if args.landscape else "portrait"
    print(f"Calendar {ls} \u2013 {le}: {len(weeks)} weeks, {len(pages_)} page(s) \u00d7 {rows} rows, {args.paper.upper()} {orient}")
    generate_pdf(pages_, start_ym, end_ym, base+".pdf", pw, ph, entries)
    generate_ps (pages_, start_ym, end_ym, base+".ps",  pw, ph, entries)

if __name__ == "__main__":
    main()