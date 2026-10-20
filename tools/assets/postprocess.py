#!/usr/bin/env python3
"""Post-process the rendered PNGs in ./out into the site's binary assets.

Article assets are driven by src/articles/<dir>/article.json:

    {"slug": "<slug>", "figures": ["fig-1-...", "fig-2-...", "fig-3-..."],
     "og_default": true}

`figures[i]` is written to images/blog/<slug>/<figures[i]>.webp from the render
out/<slug>--fig{i+1}.png; `og_default: true` additionally refreshes the generic
OG card (assets/og/article-default*) from that article's out/<slug>--og.png.

Targets (relative to DIST_ROOT, which defaults to the repo root):
  images/blog/<slug>/<figures[i]>.webp, cover.webp, og.png
  assets/og/default.png, default@2x.png, article-default.png, article-default@2x.png
  assets/logo/startupbase-mark.svg, -mark-512.png, -mark-128.png,
              -logo-dark@1x.png, -logo-dark@2x.png,
              -logo-light@1x.png, -logo-light@2x.png, -app-icon-512.png
  favicon.ico, favicon-32.png, favicon-64.png, apple-touch-icon.png

SLUG env var limits the run to one article (folder name or slug); empty = all.
"""
import json
import os
import shutil
from PIL import Image

OUT = "out"
DIST = os.environ.get("DIST_ROOT", "..")
ONLY = (os.environ.get("SLUG") or "").strip()
ARTICLES = os.path.join("src", "articles")

FIG = (2880, 1620)
OG2X = (2400, 1260)


def _mkdir(p):
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)


def _dst(rel):
    return os.path.join(DIST, rel)


def webp(src, rel, q=90, expect=None):
    im = Image.open(os.path.join(OUT, src)).convert("RGB")
    if expect and im.size != expect:
        raise SystemExit(f"{rel}: unexpected render size {im.size}, expected {expect}")
    p = _dst(rel)
    _mkdir(p)
    im.save(p, "WEBP", quality=q, method=6)
    print(f"{rel}: {im.size[0]}x{im.size[1]} {os.path.getsize(p) // 1024} KB")


def png(src, rel, size=None, trim=False):
    im = Image.open(os.path.join(OUT, src)).convert("RGBA")
    if trim:
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
    if size:
        im = im.resize(size, Image.LANCZOS)
    p = _dst(rel)
    _mkdir(p)
    im.save(p, "PNG", optimize=True)
    print(f"{rel}: {im.size[0]}x{im.size[1]} {os.path.getsize(p) // 1024} KB")
    return im


def png_fit(src, rel, box=(312, 48), trim=True):
    """Contain-fit inside `box` on a transparent canvas, keeping the ink aspect ratio."""
    im = Image.open(os.path.join(OUT, src)).convert("RGBA")
    if trim:
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
    bw, bh = box
    s = min(bw / im.width, bh / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    canvas = Image.new("RGBA", box, (0, 0, 0, 0))
    canvas.paste(im, ((bw - im.width) // 2, (bh - im.height) // 2), im)
    p = _dst(rel)
    _mkdir(p)
    canvas.save(p, "PNG", optimize=True)
    print(f"{rel}: {canvas.size[0]}x{canvas.size[1]} (ink {im.size[0]}x{im.size[1]}) {os.path.getsize(p) // 1024} KB")
    return canvas


def articles():
    """[(dir, slug, meta)] for every src/articles/<dir>/article.json (after the SLUG filter)."""
    found = []
    if not os.path.isdir(ARTICLES):
        return found
    for d in sorted(os.listdir(ARTICLES)):
        cfg = os.path.join(ARTICLES, d, "article.json")
        if not os.path.isfile(cfg):
            continue
        with open(cfg, encoding="utf-8") as fh:
            meta = json.load(fh)
        slug = meta.get("slug") or d
        if ONLY and ONLY not in (d, slug):
            continue
        found.append((d, slug, meta))
    if ONLY and not found:
        raise SystemExit(f"SLUG={ONLY}: no src/articles/*/article.json matches this slug")
    return found


# ---------- article figures + cover (16:9) + per-article OG card ----------
for _dir, slug, meta in articles():
    img = os.path.join("images", "blog", slug)

    figures = meta.get("figures") or []
    for i, fig in enumerate(figures, start=1):
        webp(f"{slug}--fig{i}.png", f"{img}/{fig}.webp", expect=FIG)

    webp(f"{slug}--cover.png", f"{img}/cover.webp", q=88, expect=FIG)

    og_src = f"{slug}--og.png"
    im = Image.open(os.path.join(OUT, og_src))
    if im.size != OG2X:
        raise SystemExit(f"{og_src}: unexpected render size {im.size}, expected {OG2X}")
    png(og_src, f"{img}/og.png", size=(1200, 630))

    # только статья, помеченная og_default, обновляет общую OG-карточку блога
    if meta.get("og_default"):
        png(og_src, "assets/og/article-default@2x.png")
        png(og_src, "assets/og/article-default.png", size=(1200, 630))

# ---------- blog OG card ----------
im = Image.open(os.path.join(OUT, "og-blog@2x.png"))
if im.size != OG2X:
    raise SystemExit(f"og-blog@2x.png: unexpected render size {im.size}, expected {OG2X}")
png("og-blog@2x.png", "assets/og/default@2x.png")
png("og-blog@2x.png", "assets/og/default.png", size=(1200, 630))

# ---------- logo lockups ----------
png("logo-dark@2x.png", "assets/logo/startupbase-logo-dark@2x.png", trim=True)
png("logo-light@2x.png", "assets/logo/startupbase-logo-light@2x.png", trim=True)
png_fit("logo-dark@2x.png", "assets/logo/startupbase-logo-dark@1x.png", box=(312, 48))
png_fit("logo-light@2x.png", "assets/logo/startupbase-logo-light@1x.png", box=(312, 48))

# ---------- brand mark (M4) ----------
shutil.copyfile("src/mark-m4.svg", _dst("assets/logo/startupbase-mark.svg"))
print("assets/logo/startupbase-mark.svg: M4 svg %d B" % os.path.getsize(_dst("assets/logo/startupbase-mark.svg")))

# render.js renders src/mark-512.html — the M4 svg scaled to the whole 512x512 canvas,
# so this PNG is 1024x1024 of real vector ink. Always resize DOWN (never upscale).
mark = Image.open(os.path.join(OUT, "mark-m4-512.png")).convert("RGBA")
print("mark source: %dx%d" % mark.size)
assert min(mark.size) >= 512, "mark source too small: %r" % (mark.size,)


def mark_png(size, rel, opaque=False):
    im = mark.resize((size, size), Image.LANCZOS)
    if opaque:  # iOS/Android mask the corners themselves -> pre-fill with --bg-0
        plate = Image.new("RGBA", (size, size), (5, 8, 7, 255))
        plate.alpha_composite(im)
        im = plate
    p = _dst(rel)
    _mkdir(p)
    im.save(p, "PNG", optimize=True)
    print(f"{rel}: {size}x{size} {os.path.getsize(p) // 1024} KB")


mark_png(512, "assets/logo/startupbase-mark-512.png")
mark_png(128, "assets/logo/startupbase-mark-128.png")
png("app-icon.png", "assets/logo/startupbase-app-icon-512.png", size=(512, 512), trim=True)
mark_png(180, "apple-touch-icon.png", opaque=True)

# ---------- favicons ----------
mark_png(64, "favicon-64.png")
mark_png(32, "favicon-32.png")
mark64 = mark.resize((64, 64), Image.LANCZOS)
ico_path = _dst("favicon.ico")
_mkdir(ico_path)
mark64.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print("favicon.ico: %d KB" % (os.path.getsize(ico_path) // 1024))

print("\nwritten under", os.path.abspath(DIST))
