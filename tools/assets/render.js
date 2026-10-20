#!/usr/bin/env node
'use strict';
/* Render the startupbase.uno image assets from the HTML templates in ./src.
   Shared templates live in ./src, article templates in ./src/articles/<slug>/.
   Reproduces the local build geometry: CSS viewport size x deviceScaleFactor 2. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SRC = path.resolve(__dirname, 'src');
const ARTICLES_DIR = path.join(SRC, 'articles');
const OUT = path.resolve(__dirname, 'out');

// shared, article-independent jobs: [template, width, height, scale, outName, transparent]
const SHARED_JOBS = [
  ['og-blog.html',    1200, 630, 2, 'og-blog@2x.png',   false],
  ['logo-dark.html',   900, 160, 2, 'logo-dark@2x.png', true],
  ['logo-light.html',  900, 160, 2, 'logo-light@2x.png', true],
  ['mark-512.html',    512, 512, 2, 'mark-m4-512.png',  true],
  ['appicon.html',     512, 512, 2, 'app-icon.png',     false],
];

// per-article templates: [file, width, height, png suffix]
// -> out/<slug>--<suffix>.png, where <slug> comes from src/articles/<dir>/article.json
const ARTICLE_JOBS = [
  ['fig1.html',  1440, 810, 'fig1'],
  ['fig2.html',  1440, 810, 'fig2'],
  ['fig3.html',  1440, 810, 'fig3'],
  ['cover.html', 1440, 810, 'cover'],
  ['og.html',    1200, 630, 'og'],
];

function readArticles() {
  if (!fs.existsSync(ARTICLES_DIR)) return [];
  return fs
    .readdirSync(ARTICLES_DIR, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort()
    .filter((dir) => fs.existsSync(path.join(ARTICLES_DIR, dir, 'article.json')))
    .map((dir) => ({
      dir,
      meta: JSON.parse(fs.readFileSync(path.join(ARTICLES_DIR, dir, 'article.json'), 'utf8')),
    }));
}

(async () => {
  const only = (process.env.SLUG || '').trim();

  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });

  const jobs = [];
  let matched = 0;
  for (const { dir, meta } of readArticles()) {
    const slug = meta.slug || dir;
    if (only && only !== dir && only !== slug) continue;
    matched += 1;
    for (const [file, w, h, suffix] of ARTICLE_JOBS) {
      if (!fs.existsSync(path.join(ARTICLES_DIR, dir, file))) continue;
      jobs.push([path.join('articles', dir, file), w, h, 2, `${slug}--${suffix}.png`, false]);
    }
  }
  for (const job of SHARED_JOBS) jobs.push(job);

  if (only && matched === 0) {
    throw new Error(`SLUG=${only}: no src/articles/*/article.json matches this slug`);
  }

  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'],
  });

  for (const [tpl, w, h, scale, name, transparent] of jobs) {
    const ctx = await browser.newContext({
      viewport: { width: w, height: h },
      deviceScaleFactor: scale,
    });
    const page = await ctx.newPage();
    await page.goto('file://' + path.join(SRC, tpl), { waitUntil: 'load' });
    // make sure webfont/installed fonts are resolved before shooting
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(250);
    await page.screenshot({
      path: path.join(OUT, name),
      omitBackground: transparent,
      fullPage: false,
    });
    const size = fs.statSync(path.join(OUT, name)).size;
    console.log(`${name}: ${w}x${h}@${scale} -> ${size} B`);
    await ctx.close();
  }

  await browser.close();
  console.log(`render done: ${matched} article(s), ${jobs.length} job(s)`);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
