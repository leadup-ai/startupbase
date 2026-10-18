#!/usr/bin/env python3
"""Post-process the rendered PNGs in ./out into the site's binary assets.

Targets (relative to DIST_ROOT, which defaults to the repo root):
  images/blog/<SLUG>/fig-1-architecture.webp, fig-2-terminal.webp,
                      fig-3-benchmarks.webp, cover.webp, og.png
  assets/og/default.png, default@2x.png, article-default.png, article-default@2x.png
  assets/logo/startupbase-mark.svg, -mark-512.png, -mark-128.png,
              -logo-dark@1x.png, -logo-dark@2x.png,
              -logo-light@1x.png, -logo-light@2x.png, -app-icon-512.png
  favicon.ico, favicon-32.png, favicon-64.png, apple-touch-icon.png
"""
import os
import shutil
from PIL import Image

OUT = "out"
DIST = os.environ.get("DIST_ROOT", "..")
SLUG = os.environ.get("SLUG", "meta-muse-spark-open-weights-agents")
IMG = os.path.join("images", "blog", SLUG)


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


# ---------- article figures + cover (16:9) ----------
FIG = (2880, 1620)
webp("fig-1-architecture.png", f"{IMG}/fig-1-architecture.webp", expect=FIG)
webp("fig-2-terminal.png", f"{IMG}/fig-2-terminal.webp", expect=FIG)
webp("fig-3-benchmarks.png", f"{IMG}/fig-3-benchmarks.webp", expect=FIG)
webp("cover.png", f"{IMG}/cover.webp", q=88, expect=FIG)

# ---------- OG cards ----------
OG2X = (2400, 1260)
for src in ("og-article@2x.png", "og-blog@2x.png"):
    im = Image.open(os.path.join(OUT, src))
    if im.size != OG2X:
        raise SystemExit(f"{src}: unexpected render size {im.size}, expected {OG2X}")
png("og-article@2x.png", "assets/og/article-default@2x.png")
png("og-article@2x.png", "assets/og/article-default.png", size=(1200, 630))
png("og-article@2x.png", f"{IMG}/og.png", size=(1200, 630))
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
