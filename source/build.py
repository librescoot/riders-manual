#!/usr/bin/env python3
"""Builds the illustrated A5 Librescoot Rider's Manual PDFs.

Supports multiple languages under source/<lang>/ with shared vector drawings,
icons, fonts and stylesheet under source/.

Usage:
  python3 source/build.py [--lang de|en|all] [--strict] [--no-previews] [--out-dir dist] [full|sample|all]
"""
import argparse
import html as H
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
WEB = ROOT / "inputs" / "website"
FONTS = ["inter-latin.woff2", "inter-latin-ext.woff2", "abel-latin.woff2"]

# Callout markers: (number, anchor x, y, circle center x, y) in SVG coordinates
CALLOUTS = {
    "ref-seitenansicht": dict(r=15, fs=17, sw=1.3, items=[
        (1, 364, 40, 290, 32), (2, 360, 128, 290, 108), (3, 396, 138, 470, 100),
        (4, 357, 270, 440, 232), (5, 650, 276, 650, 212), (6, 823, 297, 902, 250),
        (7, 800, 392, 906, 342), (8, 906, 444, 936, 404), (9, 872, 562, 934, 578),
        (10, 596, 459, 612, 560), (11, 532, 518, 532, 572), (12, 432, 465, 420, 570),
        (13, 150, 546, 112, 588), (14, 241, 418, 150, 368), (15, 266, 316, 176, 300),
        (16, 243, 262, 176, 236)]),
    "ref-lenker": dict(r=19, fs=21, sw=1.6, items=[
        (1, 206, 152, 150, 200), (2, 380, 233, 330, 330), (3, 380, 251, 420, 330),
        (4, 647, 147, 647, 48), (5, 647, 350, 740, 365), (6, 910, 248, 930, 330),
        (7, 1010, 220, 1080, 300), (8, 1090, 152, 1170, 200), (9, 1090, 60, 1176, 14)]),
    "dbc": dict(r=13, fs=15, sw=1.2, items=[
        (1, 27, 156, -24, 156), (2, 174, 18, 174, -16), (3, 321, 156, 372, 156)]),
    "anatomie": dict(r=17, fs=19, sw=1.4, items=[
        (1, 4, 20, -36, 20), (2, 240, 4, 240, -38), (3, 477, 20, 516, 20),
        (4, 92, 250, -36, 250), (5, 342, 393, 516, 393), (6, 8, 398, -36, 398),
        (7, 4, 458, -36, 458)]),
}

FORBIDDEN = {
    "\u2013": "en-dash", "\u2014": "em-dash", "\u2192": "arrow", "\u2190": "arrow",
    "\u21d2": "arrow", "\u201e": "curly-quote", "\u201c": "curly-quote",
    "\u201d": "curly-quote", "\u2018": "curly-apostrophe", "\u2019": "curly-apostrophe",
}

CHECK_SCRIPT = """
<pre id="check-result" hidden></pre>
<script>
(function () {
  if (location.hash !== "#check") return;
  function run() {
    var res = { pages: [] };
    document.querySelectorAll(".page").forEach(function (pg) {
      var body = pg.querySelector(".body"), b = body.getBoundingClientRect();
      var issues = [], maxBottom = b.top;
      body.querySelectorAll("*").forEach(function (el) {
        if (el.closest("svg") && el.tagName.toLowerCase() !== "svg") return;
        var r = el.getBoundingClientRect();
        if (!r.width && !r.height) return;
        maxBottom = Math.max(maxBottom, r.bottom);
        if (r.bottom > b.bottom + 0.5 || r.right > b.right + 0.5 || r.left < b.left - 0.5 || r.top < b.top - 0.5)
          issues.push(el.tagName + "." + el.className + " " + (el.textContent || "").trim().slice(0, 40));
        var cs = getComputedStyle(el);
        if (el.scrollWidth > el.clientWidth + 1 && cs.overflowX !== "visible" && el.tagName !== "svg")
          issues.push("scroll-x " + el.tagName + "." + el.className);
      });
      var folio = pg.querySelector(".folio");
      if (folio && folio.getBoundingClientRect().top < b.bottom) issues.push("folio overlaps body");
      res.pages.push({ page: pg.dataset.page, issues: issues, todos: pg.querySelectorAll(".todo").length,
        fill: Math.round((maxBottom - b.top) / (b.bottom - b.top) * 100) });
    });
    var pre = document.getElementById("check-result");
    pre.textContent = JSON.stringify(res);
  }
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () { setTimeout(run, 300); });
})();
</script>
</body>
</html>
"""


def find_chrome():
    env_chrome = os.environ.get("CHROME")
    if env_chrome and Path(env_chrome).exists():
        return env_chrome
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("Chrome/Chromium not found; set CHROME=/path/to/chromium")


def svg_inline(lang_dir, name, variant=None):
    lang_svg = lang_dir / "svg" / f"{name}.svg"
    svg_path = lang_svg if lang_svg.exists() else (SRC / "svg" / f"{name}.svg")
    s = svg_path.read_text(encoding="utf-8")
    s = re.sub(r"<\?xml[^>]*\?>", "", s).strip()
    if variant == "reverse":
        s = s.replace("marker-end=", "marker-start=")
    if variant:
        s = re.sub(r'id="(ah-[a-z]+)"', lambda m: f'id="{m.group(1)}-{variant}"', s)
        s = re.sub(r'url\(#(ah-[a-z]+)\)', lambda m: f'url(#{m.group(1)}-{variant})', s)
    c = CALLOUTS.get(name) if variant != "plain" else None
    if c:
        g = ['<g class="callouts">']
        for n, ax, ay, cx, cy in c["items"]:
            g.append(f'<line class="halo" x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke-width="{c["sw"]*3.2}"/>')
            g.append(f'<line class="lead-line" x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke-width="{c["sw"]}"/>')
            g.append(f'<circle class="dot" cx="{ax}" cy="{ay}" r="{c["sw"]*2.2}"/>')
        for n, ax, ay, cx, cy in c["items"]:
            g.append(f'<circle class="c" cx="{cx}" cy="{cy}" r="{c["r"]}"/>')
            g.append(f'<text x="{cx}" y="{cy + 0.5}" font-size="{c["fs"]}">{n}</text>')
        g.append("</g>")
        s = s[: s.rfind("</svg>")] + "\n".join(g) + "\n</svg>"
    s = s.replace("<svg ", f'<svg role="img" aria-label="{name}" ', 1)
    return s


def icon_inline(name, index):
    s = (SRC / "icons" / f"{name}.svg").read_text(encoding="utf-8").strip()
    for ident in re.findall(r'\bid="([^"]+)"', s):
        unique = f"icon-{index}-{ident}"
        s = s.replace(f'id="{ident}"', f'id="{unique}"')
        s = s.replace(f'url(#{ident})', f'url(#{unique})')
        s = s.replace(f'href="#{ident}"', f'href="#{unique}"')
    return s


def menu(m):
    parts = [H.unescape(p.strip()) for p in m.group(1).split(">")]
    inner = '<span class="sep" aria-hidden="true"></span>'.join(H.escape(p) for p in parts)
    return f'<span class="menu" aria-label="{H.escape(" > ".join(parts))}">{inner}</span>'


def html_shell(lang, title, body_html):
    return (
        f'<!DOCTYPE html>\n<html lang="{H.escape(lang)}">\n<head>\n<meta charset="utf-8">\n'
        f'<title>{H.escape(title)}</title>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<link rel="stylesheet" href="style.css">\n</head>\n<body>\n'
        f'{body_html}\n{CHECK_SCRIPT}'
    )


def load_source(lang_dir, cfg, target):
    if target == "full":
        parts = [p.read_text(encoding="utf-8") for p in sorted((lang_dir / "chapters").glob("*.html"))]
        if not parts:
            raise SystemExit(f"No chapter HTML files found in {lang_dir / 'chapters'}")
        return html_shell(cfg["lang"], cfg["title"], "\n".join(parts))
    sample_path = lang_dir / "sample.html"
    if not sample_path.exists():
        return None
    raw = sample_path.read_text(encoding="utf-8")
    # Allow sample.html to be either full document or page sections
    if "<body>" in raw:
        body = raw[raw.index("<body>") + len("<body>"):]
        if '<pre id="check-result"' in body:
            body = body[:body.index('<pre id="check-result"')]
        elif "</body>" in body:
            body = body[:body.index("</body>")]
        return html_shell(cfg["lang"], cfg["sample_title"], body.strip())
    return html_shell(cfg["lang"], cfg["sample_title"], raw)


def make_toc(pages, chapter_prefix):
    rows = []
    for i, p in enumerate(pages, start=1):
        for m in re.finditer(
            r'<div class="chapter-head" id="([^"]+)" data-toc="([^"]*)">\s*'
            r'<div class="chapter-label">([^<]*)</div>\s*<h1>(.*?)</h1>',
            p, re.S,
        ):
            ident, desc, label, title = m.groups()
            n = label.replace(chapter_prefix, "").strip()
            n = n if n.isdigit() else ""
            rows.append(
                f'<li><span class="n">{n}</span>'
                f'<span class="t">{title}<span class="d">{desc}</span></span>'
                f'<span class="p">{i}</span></li>'
            )
    return '<ol class="toc">' + "".join(rows) + "</ol>"


def build_html(src, lang_dir, cfg):
    icon_index = iter(range(10000))
    src = re.sub(r"\{\{icon:([a-z-]+)\}\}", lambda m: icon_inline(m.group(1), next(icon_index)), src)
    src = re.sub(
        r"\{\{svg:([a-z\-]+)(?:\|([a-z]+))?\}\}",
        lambda m: svg_inline(lang_dir, m.group(1), m.group(2)),
        src,
    )
    src = re.sub(r"\[\[(.+?)\]\]", menu, src)

    figs = re.findall(r'<figure[^>]*\bid="([^"]+)"', src)
    fignum = {f: i + 1 for i, f in enumerate(figs)}

    parts = re.split(r'(?=<section class="page)', src)
    head, pages = parts[0], parts[1:]
    tail = ""
    if pages:
        last = pages[-1]
        k = last.rfind("</section>") + len("</section>")
        pages[-1], tail = last[:k], last[k:]

    pageof = {}
    for i, p in enumerate(pages, start=1):
        for ident in re.findall(r'\bid="([^"]+)"', p):
            pageof.setdefault(ident, i)

    toc = make_toc(pages, cfg["chapter_prefix"])
    out = []
    for i, p in enumerate(pages, start=1):
        p = p.replace("{{toc}}", toc)
        side = "recto" if i % 2 else "verso"
        p = p.replace('<section class="page', f'<section data-page="{i}" class="page {side}', 1)
        m = re.search(r'data-folio="([^"]*)"', p)
        if m and m.group(1):
            fol = f'<div class="folio"><span>{m.group(1)}</span><b>{i}</b></div>'
            k = p.rfind("</section>")
            p = p[:k] + fol + p[k:]
        out.append(p)
    doc = head + "".join(out) + tail

    missing = []
    page_prefix = cfg["page_prefix"]
    fig_prefix = cfg["fig_prefix"]

    def ref_page(m):
        k = m.group(1)
        if k not in pageof:
            missing.append(k)
            return f"{page_prefix} ??"
        return f"{page_prefix}&nbsp;{pageof[k]}"

    def ref_pn(m):
        k = m.group(1)
        if k not in pageof:
            missing.append(k)
            return "??"
        return str(pageof[k])

    def ref_fig(m):
        k = m.group(1)
        if k not in fignum:
            missing.append(k)
            return f"{fig_prefix} ??"
        return f"{fig_prefix}&nbsp;{fignum[k]}"

    doc = re.sub(r"\{\{p:([a-z0-9\-]+)\}\}", ref_page, doc)
    doc = re.sub(r"\{\{pn:([a-z0-9\-]+)\}\}", ref_pn, doc)
    doc = re.sub(r"\{\{fig:([a-z0-9\-]+)\}\}", ref_fig, doc)
    leftovers = re.findall(r"\{\{[^}]*\}\}|\[\[[^\]]*\]\]", doc)
    return doc, len(pages), fignum, missing, leftovers


def text_checks(doc):
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", doc, flags=re.S)
    text = H.unescape(re.sub(r"<[^>]+>", " ", body))
    found = {name: text.count(ch) for ch, name in FORBIDDEN.items() if ch in text}
    words = {w: len(re.findall(w, text)) for w in ["LibreScoot", "libreScoot", "Libre Scoot"] if re.search(w, text)}
    return found, words


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"Command failed: {' '.join(map(str, cmd))}")
    return r


def check_fonts_embedded(pdffonts_output):
    unembedded = []
    for line in pdffonts_output.splitlines()[2:]:
        if not line.strip():
            continue
        if not re.search(r"\syes\s+yes\s+yes\s+\d+\s+\d+$", line):
            unembedded.append(line.strip())
    return unembedded


def discover_languages():
    langs = []
    for d in sorted(SRC.iterdir()):
        if d.is_dir() and (d / "lang.json").exists() and list((d / "chapters").glob("*.html")):
            langs.append(d.name)
    return langs


def build_one(lang, target, out_dir, chrome, previews=True, strict=False, version=None):
    lang_dir = SRC / lang
    cfg = json.loads((lang_dir / "lang.json").read_text(encoding="utf-8"))
    src = load_source(lang_dir, cfg, target)
    if src is None:
        return None

    html_dir = ROOT / "tmp" / "build" / lang / "html"
    tmp_dir = ROOT / "tmp" / "build" / lang
    prev_dir = out_dir / "previews" / f"{lang}-{target}"
    out_dir.mkdir(parents=True, exist_ok=True)
    for d in (html_dir / "assets/img", html_dir / "assets/fonts", tmp_dir):
        d.mkdir(parents=True, exist_ok=True)

    for name, rel in cfg["images"].items():
        src_img = ROOT / rel
        if not src_img.exists():
            raise SystemExit(f"Missing image asset for {lang}: {src_img}")
        shutil.copy2(src_img, html_dir / "assets/img" / name)
    for f in FONTS:
        shutil.copy2(WEB / "fonts" / f, html_dir / "assets/fonts" / f)
    shutil.copy2(SRC / "style.css", html_dir / "style.css")

    doc, npages, fignum, missing, leftovers = build_html(src, lang_dir, cfg)
    html_name = f"{lang}-{target}.html"
    base_pdf_name = cfg["pdf_name"] if target == "full" else cfg["sample_pdf_name"]
    if version:
        stem, ext = os.path.splitext(base_pdf_name)
        pdf_name = f"{stem}-{version}{ext}"
    else:
        pdf_name = base_pdf_name
    html_file = html_dir / html_name
    html_file.write_text(doc, encoding="utf-8")
    forb, words = text_checks(doc)

    prof = tmp_dir / "chrome-profile"
    base = [
        chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
        f"--user-data-dir={prof}", "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
    ]
    pdf = out_dir / pdf_name
    run(base + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", html_file.as_uri()], timeout=180)
    dom = run(base + ["--dump-dom", html_file.as_uri() + "#check"], timeout=180).stdout
    m = re.search(r'<pre id="check-result"[^>]*>(.*?)</pre>', dom, re.S)
    geo = json.loads(H.unescape(m.group(1))) if m else {"error": "missing check result in DOM"}

    info = run(["pdfinfo", str(pdf)]).stdout
    fonts = run(["pdffonts", str(pdf)]).stdout
    unembedded = check_fonts_embedded(fonts)

    preview_files = []
    if previews:
        prev_dir.mkdir(parents=True, exist_ok=True)
        for old in prev_dir.glob("*.png"):
            old.unlink()
        run(["pdftoppm", "-r", "150", "-png", str(pdf), str(prev_dir / "page")])
        pngs = sorted(prev_dir.glob("page-*.png"))
        tiles = "6x2" if len(pngs) <= 12 else "8x"
        run([
            "montage", *map(str, pngs), "-tile", tiles,
            "-geometry", "420x596+14+14", "-background", "#8d9497",
            str(prev_dir / "contact-sheet.png"),
        ])
        preview_files = [p.name for p in sorted(prev_dir.glob("*.png"))]

    geo_issues = [
        {"page": p["page"], "issues": p["issues"]}
        for p in geo.get("pages", [])
        if p.get("issues")
    ]
    todos = sum(p.get("todos", 0) for p in geo.get("pages", []))
    report = {
        "lang": lang,
        "target": target,
        "pdf": str(pdf.relative_to(ROOT)),
        "pages": npages,
        "todos": todos,
        "figures": len(fignum),
        "missing_refs": missing,
        "leftover_placeholders": leftovers,
        "forbidden_chars": forb,
        "brand_spelling_errors": words,
        "geometry_issues": geo_issues,
        "unembedded_fonts": unembedded,
        "pdfinfo": info,
        "previews": preview_files,
    }
    (tmp_dir / f"report-{target}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {k: v for k, v in report.items() if k not in ("pdfinfo", "previews")}
    print(json.dumps(summary, ensure_ascii=False))

    if strict:
        failures = []
        if "error" in geo:
            failures.append(f"geometry check error: {geo['error']}")
        if geo_issues:
            failures.append(f"geometry overflow on pages: {geo_issues}")
        if missing:
            failures.append(f"missing refs: {missing}")
        if leftovers:
            failures.append(f"leftover placeholders: {leftovers}")
        if forb:
            failures.append(f"forbidden chars: {forb}")
        if words:
            failures.append(f"brand spelling errors: {words}")
        if todos:
            failures.append(f"remaining TODO boxes: {todos}")
        if unembedded:
            failures.append(f"unembedded fonts: {unembedded}")
        if failures:
            raise SystemExit(f"Strict check failed for {lang}/{target}:\n  - " + "\n  - ".join(failures))
    return report


def main():
    parser = argparse.ArgumentParser(description="Build Librescoot Rider's Manual PDFs.")
    parser.add_argument("target", nargs="?", default="all",
                        choices=["full", "sample", "all", "gesamt", "muster"],
                        help="Build target (default: all)")
    parser.add_argument("--lang", default="all", help="Language code (e.g. de, en) or 'all'")
    parser.add_argument("--out-dir", default="dist", help="Output directory relative to repo root")
    parser.add_argument("--no-previews", action="store_true", help="Skip PNG preview rendering")
    parser.add_argument("--strict", action="store_true", help="Fail on any layout, ref, text or font issue")
    parser.add_argument("--version", default=None, help="Optional version suffix for output PDF filenames (e.g. 1.4.3)")
    args = parser.parse_args()

    target_map = {"gesamt": ["full"], "full": ["full"], "muster": ["sample"], "sample": ["sample"], "all": ["full", "sample"]}
    targets = target_map[args.target]
    langs = discover_languages() if args.lang == "all" else [args.lang]
    if not langs:
        raise SystemExit("No buildable languages found under source/<lang>/chapters/")

    chrome = find_chrome()
    run([sys.executable, str(SRC / "extract_icons.py")])
    out_dir = ROOT / args.out_dir

    for lang in langs:
        for t in targets:
            build_one(lang, t, out_dir, chrome, previews=not args.no_previews, strict=args.strict, version=args.version)


if __name__ == "__main__":
    main()
